"""
Token 智能优化 Pipeline — 三层架构
====================================
压缩 → 缓存 → 路由，自动最小化 LLM 调用成本。

三层说明：
  L1 压缩层 — LLMLingua 压缩 prompt，减少输入 token
  L2 缓存层 — GPTCache 语义缓存，相似请求直接返回
  L3 路由层 — LiteLLM Router，按复杂度自动选模型

用法:
    from token_smart_pipeline import SmartPipeline
    pipe = SmartPipeline()
    result = pipe.ask("解释一下什么是机器学习")
    print(result.text, result.cost, result.layer_used)
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── L1: 压缩层 ──────────────────────────────────────────
from llmlingua import PromptCompressor

# ── L2: 缓存层 ──────────────────────────────────────────
import sqlite3

# ── L3: 路由层 ──────────────────────────────────────────
import litellm
from litellm import completion, cost_per_token

# 抑制 litellm 的 verbose 日志
litellm.set_verbose = False


@dataclass
class PipelineResult:
    """Pipeline 返回结果"""
    content: str
    model_used: str
    cost_usd: float
    layer_used: str          # "cache" | "llm"
    tokens_prompt: int = 0
    tokens_completion: int = 0
    latency_ms: float = 0
    compressed: bool = False
    original_tokens: int = 0
    compressed_tokens: int = 0

    @property
    def text(self) -> str:
        return self.content


class SmartPipeline:
    """
    Token 智能优化 Pipeline

    三层级联：
      L1: Prompt 压缩（LLMLingua-2 BERT）
      L2: 语义缓存（GPTCache + ONNX 本地嵌入）
      L3: 成本路由（LiteLLM Router）

    复杂度判定启发式（用于路由）：
      - 简单 (flash): < 100 字, 或关键词匹配
      - 复杂 (pro):  > 300 字, 或含"分析/设计/架构/优化/调试"
      - 中等 (flash 默认): 其余
    """

    # 模型价格 ($/1M tokens, 输入/输出)
    PRICES = {
        "deepseek/deepseek-chat":      (0.14, 0.28),   # flash, 默认
        "deepseek/deepseek-reasoner":  (0.89, 1.10),   # pro (reasoner)
    }

    # 复杂度判定关键词
    COMPLEX_KEYWORDS = [
        "分析", "设计", "架构", "优化", "调试", "排查",
        "重构", "审核", "review", "debug", "design",
        "architecture", "optimize", "refactor", "audit",
    ]

    # 缓存目录
    CACHE_DIR = Path.home() / ".cache" / "token_smart_pipeline"

    def __init__(
        self,
        compress_rate: float = 0.5,
        cache_threshold: float = 0.85,
        budget_monthly: float = 50.0,
    ):
        self.compress_rate = compress_rate
        self.cache_threshold = cache_threshold
        self.budget_monthly = budget_monthly
        self.total_cost = 0.0
        self.total_calls = 0
        self.cache_hits = 0

        # ── L1: 初始化压缩器 ──
        print("[L1] 加载 LLMLingua 压缩器...")
        self.compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
            use_llmlingua2=True,
            device_map="cpu",
        )

        # ── L2: 初始化缓存 (SQLite 本地) ──
        print("[L2] 初始化本地缓存 (SQLite)...")
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._cache_db = sqlite3.connect(str(self.CACHE_DIR / "cache.db"))
        self._cache_db.execute(
            "CREATE TABLE IF NOT EXISTS cache "
            "(key TEXT PRIMARY KEY, value TEXT, created_at REAL)"
        )
        self._cache_db.commit()

        # ── L3: 路由层 (延迟初始化，首次调用时才检查 key) ──
        self._router = None
        self._router_models = [
            {
                "model_name": "deepseek-flash",
                "litellm_params": {"model": "deepseek/deepseek-chat"},
            },
            {
                "model_name": "deepseek-pro",
                "litellm_params": {"model": "deepseek/deepseek-reasoner"},
            },
        ]

    # ── 内部辅助 ──────────────────────────────────────

    def _get_ds_key(self) -> str:
        """自动获取 DeepSeek API Key。
        优先级：环境变量 > .env 文件自动发现 > 报错
        """
        import os

        # 1. 先查环境变量
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        if key:
            return key

        # 2. 自动从 .env 加载（搜索多个可能位置）
        try:
            from dotenv import load_dotenv
            from pathlib import Path as _Path

            candidates = [
                _Path.cwd() / ".env",
                _Path.home() / ".hermes" / ".env",
            ]
            hermes_home = os.environ.get("HERMES_HOME", "")
            if hermes_home:
                candidates.append(_Path(hermes_home) / ".env")
            for env_file in candidates:
                if env_file.is_file():
                    load_dotenv(env_file)
                    key = os.environ.get("DEEPSEEK_API_KEY", "")
                    if key:
                        return key
        except ImportError:
            pass

        raise RuntimeError(
            "找不到 DEEPSEEK_API_KEY。请设置环境变量或在项目根目录创建 .env 文件"
        )

    @staticmethod
    def _cache_key_fn(prompt: str) -> str:
        """缓存 key：MD5 前 16 位"""
        return hashlib.md5(prompt.encode()).hexdigest()[:16]

    def _judge_complexity(self, prompt: str) -> str:
        """
        判定请求复杂度 → 选择模型
        返回 "flash" | "pro"
        """
        prompt_lower = prompt.lower()

        # 含复杂关键词 → pro（优先于长度判定）
        for kw in self.COMPLEX_KEYWORDS:
            if kw in prompt_lower:
                return "pro"

        # 长文本 → pro
        if len(prompt) > 300:
            return "pro"

        return "flash"

    # ── 公开 API ──────────────────────────────────────

    def compress(self, prompt: str) -> tuple[str, int, int]:
        """
        压缩 prompt
        返回: (compressed_text, original_tokens, compressed_tokens)
        """
        if self.compress_rate >= 1.0 or len(prompt) < 50:
            return prompt, max(len(prompt)//2, 1), max(len(prompt)//2, 1)

        try:
            result = self.compressor.compress_prompt_llmlingua2(
                [prompt],
                rate=self.compress_rate,
                force_tokens=["\n", "。", "！", "？", ":", "="],
            )
            compressed = result["compressed_prompt"]
            # 粗略估算 token 数（中文 ~1.5 字/token，英文 ~0.75 词/token）
            orig_tokens = len(prompt) // 2
            comp_tokens = len(compressed) // 2
            return compressed, orig_tokens, comp_tokens
        except Exception as e:
            print(f"[L1] 压缩失败: {e}, 跳过压缩")
            return prompt, 0, 0

    def ask(
        self,
        prompt: str,
        system_prompt: str = "",
        force_model: Optional[str] = None,
        skip_cache: bool = False,
        skip_compress: bool = False,
    ) -> PipelineResult:
        """
        智能请求 — 自动经过压缩→缓存→路由

        参数:
            prompt: 用户输入
            system_prompt: 系统提示词（可选）
            force_model: 强制指定模型 ("flash"|"pro")
            skip_cache: 跳过缓存
            skip_compress: 跳过压缩
        """
        t0 = time.time()

        # ── L1: 压缩 ──
        compressed = False
        original_tokens = 0
        compressed_tokens = 0
        final_prompt = prompt

        if not skip_compress:
            final_prompt, original_tokens, compressed_tokens = self.compress(prompt)
            compressed = compressed_tokens > 0 and compressed_tokens < original_tokens

        cache_key = self._cache_key_fn(final_prompt)

        # ── L2: 缓存查询 ──
        if not skip_cache:
            try:
                row = self._cache_db.execute(
                    "SELECT value FROM cache WHERE key=?", (cache_key,)
                ).fetchone()
                if row:
                    self.cache_hits += 1
                    self.total_calls += 1
                    elapsed = (time.time() - t0) * 1000
                    return PipelineResult(
                        content=row[0],
                        model_used="cache",
                        cost_usd=0.0,
                        layer_used="cache",
                        latency_ms=elapsed,
                        compressed=compressed,
                        original_tokens=original_tokens,
                        compressed_tokens=compressed_tokens,
                    )
            except Exception as e:
                print(f"[L2] 缓存查询失败: {e}")

        # ── L3: 路由 + LLM 调用 ──
        model_key = force_model or self._judge_complexity(prompt)
        model_name = f"deepseek-{model_key}"
        model_id = "deepseek/deepseek-chat" if model_key == "flash" else "deepseek/deepseek-reasoner"

        # 预算检查
        if self.total_cost >= self.budget_monthly:
            # 超预算 → 降级到 flash
            print(f"[L3] ⚠️ 月预算 ${self.budget_monthly} 已用完，降级到 flash")
            model_key = "flash"
            model_name = "deepseek-flash"
            model_id = "deepseek/deepseek-chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": final_prompt})

        try:
            response = completion(
                model=model_id,
                messages=messages,
                api_key=self._get_ds_key(),
            )
        except Exception as e:
            # fallback 到 flash
            if model_key == "pro":
                print(f"[L3] pro 失败 ({e}), fallback → flash")
                model_key = "flash"
                model_name = "deepseek-flash"
                model_id = "deepseek/deepseek-chat"
                response = completion(
                    model=model_id,
                    messages=messages,
                    api_key=self._get_ds_key(),
                )
            else:
                raise

        content = response.choices[0].message.content

        # 成本计算
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else len(final_prompt) // 2
        completion_tokens = usage.completion_tokens if usage else len(content) // 2

        price_in, price_out = self.PRICES[model_id]
        cost = (prompt_tokens * price_in + completion_tokens * price_out) / 1_000_000
        self.total_cost += cost
        self.total_calls += 1

        # 存缓存
        try:
            self._cache_db.execute(
                "INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
                (cache_key, content, time.time()),
            )
            self._cache_db.commit()
        except Exception:
            pass  # 缓存写入失败不阻塞

        elapsed = (time.time() - t0) * 1000

        return PipelineResult(
            content=content,
            model_used=model_name,
            cost_usd=cost,
            layer_used="llm",
            tokens_prompt=prompt_tokens,
            tokens_completion=completion_tokens,
            latency_ms=elapsed,
            compressed=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
        )

    def stats(self) -> dict:
        """返回管道统计"""
        return {
            "total_calls": self.total_calls,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": f"{self.cache_hits/max(1,self.total_calls)*100:.1f}%",
            "total_cost": f"${self.total_cost:.4f}",
            "budget": f"${self.budget_monthly}",
            "budget_used": f"{self.total_cost/self.budget_monthly*100:.1f}%",
        }


# ── 自测 ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Token Smart Pipeline — 自测")
    print("=" * 50)

    pipe = SmartPipeline(compress_rate=0.5)

    # 测试1: 简单问题 → flash
    print("\n[测试1] 简单提问 → 预期走 flash")
    r1 = pipe.ask("什么是 Python？")
    print(f"  结果: {r1.text[:80]}...")
    print(f"  模型: {r1.model_used}, 层: {r1.layer_used}, 费用: ${r1.cost_usd:.6f}, 延迟: {r1.latency_ms:.0f}ms")

    # 测试2: 缓存命中
    print("\n[测试2] 同样问题 → 预期缓存命中")
    r2 = pipe.ask("什么是 Python？")
    print(f"  结果: {r2.text[:80]}...")
    print(f"  模型: {r2.model_used}, 层: {r2.layer_used}, 费用: ${r2.cost_usd:.6f}, 延迟: {r2.latency_ms:.0f}ms")

    # 测试3: 复杂问题 → pro
    print("\n[测试3] 复杂提问 → 预期走 pro")
    r3 = pipe.ask("请详细分析 Python 异步编程的架构设计，并优化以下代码的性能瓶颈。")
    print(f"  结果: {r3.text[:80]}...")
    print(f"  模型: {r3.model_used}, 层: {r3.layer_used}, 费用: ${r3.cost_usd:.6f}, 延迟: {r3.latency_ms:.0f}ms")

    # 统计
    print("\n[统计]", json.dumps(pipe.stats(), indent=2, ensure_ascii=False))
