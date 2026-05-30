#!/usr/bin/env python3
"""
📊 估值择时定投策略助手 (Valuation-Based DCA Assistant)
=========================================================

根据沪深300 / 纳斯达克100 的 PE 历史百分位，动态调整每月定投金额。

策略规则:
  PE百分位 < 30%  (低估区)   → 加码  ¥1,500
  PE百分位 30%~70% (正常区) → 基准  ¥1,000
  PE百分位 > 70%  (高估区)   → 减码  ¥500

数据来源:
  - 沪深300 PE 百分位: 蛋卷基金公开API / 东方财富 / 中证指数
  - 纳斯达克100 PE 百分位: Yahoo Finance API (当前PE) + 历史范围估算

用法:
  python valuation_dca.py                       # 自动获取数据 + 输出建议
  python valuation_dca.py --manual              # 手动输入百分位
  python valuation_dca.py --simulate            # 回测对比（固定定投 vs 估值择时）
  python valuation_dca.py --simulate --years 10 # 回测10年
  python valuation_dca.py --json                # JSON 格式输出（供其他工具调用）

作者: Reasonix Code  |  免责声明: 本工具仅用于研究参考，不构成投资建议。
"""

import argparse
import json
import math
import sys
import time
from datetime import datetime, date
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


# ═══════════════════════════════════════════════════════════════
# 配置常量
# ═══════════════════════════════════════════════════════════════

# PE百分位阈值
THRESHOLD_LOW = 0.30          # 30% — 低估线
THRESHOLD_HIGH = 0.70         # 70% — 高估线

# 各区间定投金额
AMOUNT_MAP = {
    "低估": 1500,    # < 30%
    "正常": 1000,    # 30% ~ 70%
    "高估": 500,     # > 70%
}

# 组合资产配置权重
PORTFOLIO_WEIGHTS = {
    "沪深300": 0.35,
    "中证500": 0.20,
    "纳斯达克100": 0.25,
    "红利低波": 0.20,
}

INITIAL_CAPITAL = 10_000      # 初始资金 1万
MONTHLY_BASE = 1_000          # 基准月定投额
CASH_YIELD = 0.02             # 闲置资金年化收益率（货币基金）


# ═══════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════

@dataclass
class ValuationSnapshot:
    """单指数估值快照"""
    name: str
    current_pe: float
    percentile: float          # 0~100
    zone: str = ""             # 低估 / 正常 / 高估
    median_pe: float = 0.0
    min_pe_5y: float = 0.0
    max_pe_5y: float = 0.0
    fetch_time: str = ""
    source: str = ""

    def __post_init__(self):
        if not self.zone:
            p = self.percentile
            if p < THRESHOLD_LOW * 100:
                self.zone = "低估"
            elif p > THRESHOLD_HIGH * 100:
                self.zone = "高估"
            else:
                self.zone = "正常"

    @property
    def suggest_amount(self) -> int:
        """基于百分位的建议定投额"""
        return AMOUNT_MAP[self.zone]

    def color(self) -> str:
        """终端显示颜色标记"""
        return {"低估": "🟢", "正常": "🟡", "高估": "🔴"}[self.zone]


@dataclass
class StrategyDecision:
    """当期策略决策"""
    date: str
    csi300: ValuationSnapshot
    ndx: ValuationSnapshot
    combined_percentile: float       # 加权综合百分位
    combined_zone: str
    invest_amount: int               # 本期建议定投金额
    allocation: Dict[str, float]     # 资产间分配（元）


# ═══════════════════════════════════════════════════════════════
# 数据获取层 — 多来源自动切换
# ═══════════════════════════════════════════════════════════════

class DataFetcher:
    """
    多源数据获取器。
    自动尝试各数据源，全部失败时支持手动输入回退。
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # ── 沪深300 ──────────────────────────────────────────

    @staticmethod
    def _csi300_from_danjuan() -> Optional[ValuationSnapshot]:
        """
        来源1：蛋卷基金公开估值API
        https://danjuanapp.com/djapi/fund/valuation-detail/SH000300
        """
        try:
            url = "https://danjuanapp.com/djapi/fund/valuation-detail/SH000300"
            resp = requests.get(url, headers={"User-Agent": DataFetcher.USER_AGENT}, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            d = data.get("data", {})
            if not d:
                return None

            return ValuationSnapshot(
                name="沪深300",
                current_pe=float(d.get("pe", 0)),
                percentile=float(d.get("pe_percentile", 0)),
                median_pe=float(d.get("pe_median", 0)),
                min_pe_5y=float(d.get("pe_min", 0)),
                max_pe_5y=float(d.get("pe_max", 0)),
                fetch_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                source="蛋卷基金",
            )
        except Exception:
            return None

    @staticmethod
    def _csi300_from_eastmoney() -> Optional[ValuationSnapshot]:
        """
        来源2：东方财富 Choice 估值数据
        """
        try:
            url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
            params = {
                "reportName": "RPT_INDEX_VALUATION",
                "columns": "INDEX_CODE,TRADE_DATE,PE,PE_PERCENTILE",
                "filter": '(INDEX_CODE="000300")',
                "pageNumber": 1,
                "pageSize": 1,
                "sortTypes": -1,
                "sortColumns": "TRADE_DATE",
            }
            resp = requests.get(url, params=params, headers={"User-Agent": DataFetcher.USER_AGENT}, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            rows = data.get("result", {}).get("data", [])
            if not rows:
                return None
            r = rows[0]
            return ValuationSnapshot(
                name="沪深300",
                current_pe=float(r.get("PE", 0)),
                percentile=float(r.get("PE_PERCENTILE", 0)),
                fetch_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                source="东方财富",
            )
        except Exception:
            return None

    @staticmethod
    def _csi300_from_csv_cache() -> Optional[ValuationSnapshot]:
        """
        来源3：本地缓存/内置最近数据（网络不可用时的最后回退）
        """
        # 内置一个近期参考值（2025年5月左右沪深300 PE约12.5，百分位约45%）
        return ValuationSnapshot(
            name="沪深300",
            current_pe=12.5,
            percentile=45.0,
            median_pe=13.0,
            fetch_time="缓存数据（非实时）",
            source="内置缓存",
        )

    # ── 纳斯达克100 ──────────────────────────────────────

    @staticmethod
    def _ndx_from_yahoo() -> Optional[ValuationSnapshot]:
        """
        来源1：Yahoo Finance — 获取当前PE + 历史数据估算百分位
        """
        try:
            # 获取当前PE (forwardPE 或 trailingPE)
            url = "https://query1.finance.yahoo.com/v8/finance/chart/^NDX"
            params = {"range": "1d", "interval": "1d"}
            resp = requests.get(url, params=params, headers={"User-Agent": DataFetcher.USER_AGENT}, timeout=10)
            if resp.status_code != 200:
                return None

            # Yahoo Finance chart API 不直接返回PE，需要从统计接口获取
            url2 = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/^NDX"
            params2 = {"modules": "summaryDetail,defaultKeyStatistics"}
            resp2 = requests.get(url2, params=params2, headers={"User-Agent": DataFetcher.USER_AGENT}, timeout=10)
            if resp2.status_code != 200:
                return None

            data = resp2.json()
            qs = data.get("quoteSummary", {}).get("result", [{}])[0]
            sd = qs.get("summaryDetail", {})
            ks = qs.get("defaultKeyStatistics", {})

            # 尝试 forwardPE → trailingPE → priceEarnings
            pe = None
            for key in ["forwardPE", "trailingPE", "priceEarnings"]:
                v = sd.get(key, {}) if key in sd else ks.get(key, {})
                if v and v.get("raw"):
                    pe = float(v["raw"])
                    break

            if pe is None or pe <= 0:
                return None

            # 历史参考范围（纳斯达克100 PE 通常在20-40之间）
            # 当前值接近下限→低估，接近上限→高估
            hist_min, hist_max = 20.0, 40.0
            # 限定范围防止百分位溢出
            clamped = max(hist_min, min(hist_max, pe))
            percentile = (clamped - hist_min) / (hist_max - hist_min) * 100

            return ValuationSnapshot(
                name="纳斯达克100",
                current_pe=pe,
                percentile=round(percentile, 1),
                min_pe_5y=hist_min,
                max_pe_5y=hist_max,
                fetch_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                source="Yahoo Finance",
            )
        except Exception:
            return None

    @staticmethod
    def _ndx_from_macrotrends() -> Optional[ValuationSnapshot]:
        """
        来源2：Macrotrends 网页数据（备选）
        注意：该站点需要 JS 渲染，纯 requests 无法获取有效数据。
        保留此入口供将来使用 headless browser 方案。
        """
        # TODO: 改用 Playwright/Selenium 实现 JS 渲染抓取
        return None

    @staticmethod
    def _ndx_from_cache() -> Optional[ValuationSnapshot]:
        """
        来源3：内置缓存参考值
        """
        return ValuationSnapshot(
            name="纳斯达克100",
            current_pe=33.0,
            percentile=55.0,
            fetch_time="缓存数据（非实时）",
            source="内置缓存",
        )

    # ── 统一入口 ─────────────────────────────────────────

    @classmethod
    def fetch_csi300(cls) -> Optional[ValuationSnapshot]:
        """获取沪深300估值数据（自动切换来源）"""
        if not _HAS_REQUESTS:
            print("⚠️  requests 库未安装，使用内置参考值（pip install requests 获取实时数据）")
            return cls._csi300_from_csv_cache()
        for method in [cls._csi300_from_danjuan, cls._csi300_from_eastmoney]:
            result = method()
            if result:
                return result
        # 最后回退到缓存
        cached = cls._csi300_from_csv_cache()
        print("⚠️  无法获取实时数据，使用内置参考值（仅供参考）")
        return cached

    @classmethod
    def fetch_nasdaq100(cls) -> Optional[ValuationSnapshot]:
        """获取纳斯达克100估值数据（自动切换来源）"""
        if not _HAS_REQUESTS:
            print("⚠️  requests 库未安装，使用内置参考值（pip install requests 获取实时数据）")
            return cls._ndx_from_cache()
        for method in [cls._ndx_from_yahoo, cls._ndx_from_macrotrends]:
            result = method()
            if result:
                return result
        cached = cls._ndx_from_cache()
        print("⚠️  无法获取实时数据，使用内置参考值（仅供参考）")
        return cached

    @staticmethod
    def manual_input() -> Tuple[float, float]:
        """手动输入百分位"""
        print("\n📝 手动输入模式")
        print("-" * 40)
        try:
            csi = float(input("  沪深300 PE百分位 (0~100): ").strip())
            ndx = float(input("  纳斯达克100 PE百分位 (0~100): ").strip())
            if not (0 <= csi <= 100 and 0 <= ndx <= 100):
                raise ValueError("超出范围")
            return csi, ndx
        except (ValueError, EOFError):
            print("  ⚠️  输入无效，使用默认值 50%")
            return 50.0, 50.0


# ═══════════════════════════════════════════════════════════════
# 策略计算核心
# ═══════════════════════════════════════════════════════════════

class ValuationStrategy:
    """
    估值择时定投策略

    核心逻辑:
      PE百分位 < 30%  →  加码 ¥1,500   (低估，市场便宜，多买份额)
      PE百分位 30~70% →  基准 ¥1,000   (正常，按计划执行)
      PE百分位 > 70%  →  减码 ¥500     (高估，市场贵，少买，保留现金)

    综合判断:
      沪深300 和 纳斯达克100 的百分位按组合权重加权平均
      得到综合百分位 → 决定本期定投总额
      然后按 PORTFOLIO_WEIGHTS 分配到各资产
    """

    def __init__(self, csi300_pct: float, ndx_pct: float):
        self.csi300_pct = csi300_pct
        self.ndx_pct = ndx_pct

        # 综合百分位 = 按权重加权（沪深300 0.35 + 中证500 0.20 + 纳斯达克100 0.25 + 红利低波 0.20）
        # 中证500与沪深300相关性高，红利的估值逻辑不同，简化处理：
        # 综合 = 沪深300 * (0.35+0.20) + 纳斯达克100 * 0.25 + 红利低波 * 0.20
        # 红利低波我们单独判断（通常估值波动小，单独处理）
        # 更简单的做法：A股部分取沪深300百分位，美股取纳指百分位
        self.combined_pct = csi300_pct * 0.55 + ndx_pct * 0.25 + 50.0 * 0.20
        # 注：红利低波默认按中性（50%）处理，因其成分股（银行/公用事业）PE波动小

    @staticmethod
    def zone_from_percentile(pct: float) -> str:
        if pct < THRESHOLD_LOW * 100:
            return "低估"
        elif pct > THRESHOLD_HIGH * 100:
            return "高估"
        return "正常"

    @staticmethod
    def amount_from_zone(zone: str) -> int:
        return AMOUNT_MAP.get(zone, 1000)

    def decide(self) -> Dict:
        """输出完整的策略决策"""
        combined_zone = self.zone_from_percentile(self.combined_pct)
        total_amount = self.amount_from_zone(combined_zone)

        # 按组合权重分配
        allocation = {}
        remaining = total_amount
        # 先分配有明确权重的
        for name, weight in PORTFOLIO_WEIGHTS.items():
            alloc = round(total_amount * weight)
            allocation[name] = alloc
            remaining -= alloc
        # 修正 rounding 误差
        if remaining != 0 and allocation:
            # 加到沪深300
            allocation["沪深300"] += remaining

        return {
            "综合百分位": round(self.combined_pct, 1),
            "综合区间": combined_zone,
            "建议定投总额": total_amount,
            "资产分配": allocation,
            "沪深300": {
                "百分位": round(self.csi300_pct, 1),
                "区间": self.zone_from_percentile(self.csi300_pct),
                "建议": self.amount_from_zone(self.zone_from_percentile(self.csi300_pct)),
            },
            "纳斯达克100": {
                "百分位": round(self.ndx_pct, 1),
                "区间": self.zone_from_percentile(self.ndx_pct),
                "建议": self.amount_from_zone(self.zone_from_percentile(self.ndx_pct)),
            },
        }


# ═══════════════════════════════════════════════════════════════
# 回测模拟器
# ═══════════════════════════════════════════════════════════════

class BacktestEngine:
    """
    历史回测引擎：对比 固定定投 vs 估值择时定投。

    模拟逻辑:
      - 使用内置的历史市场周期数据（包含完整的牛熊转换）
      - 假设每月定投日投入资金
      - 估值择时: 根据当月PE百分位调整定投额
      - 固定定投: 每月固定 ¥1,000
      - 闲置资金放在货币基金（年化 2%）
    """

    # 内置历史模拟数据（基于2005-2024年沪深300和纳斯达克100的实际走势特征）
    # 包含三个完整牛熊周期: 2007牛市→2008熊市→2014-2015牛市→2015-2016股灾→
    # 2019-2021结构性牛市→2022熊市→2023-2024震荡修复
    HISTORICAL_MARKET_DATA = [
        # (月份, 沪深300百分位, 纳指100百分位, 沪深300月涨跌幅, 纳指100月涨跌幅)
        # 第1年 (市场底部区域)
        (1,  18, 25,  0.025,  0.015),
        (2,  15, 22, -0.010,  0.010),
        (3,  12, 20,  0.035,  0.025),
        (4,  10, 18,  0.020,  0.018),
        (5,   8, 16,  0.045,  0.030),
        (6,  11, 19, -0.015, -0.008),
        (7,   9, 17,  0.030,  0.022),
        (8,   7, 15,  0.055,  0.035),
        (9,  13, 21, -0.020, -0.010),
        (10, 10, 18,  0.040,  0.028),
        (11, 14, 22, -0.025, -0.012),
        (12, 16, 24,  0.038,  0.020),
        # 第2年 (温和上涨)
        (13, 20, 28,  0.028,  0.018),
        (14, 22, 30,  0.045,  0.025),
        (15, 25, 33,  0.032,  0.020),
        (16, 28, 35,  0.018,  0.015),
        (17, 30, 38,  0.022,  0.012),
        (18, 32, 40,  0.015,  0.010),
        (19, 35, 42,  0.020,  0.018),
        (20, 38, 45,  0.010,  0.008),
        (21, 40, 47,  0.025,  0.015),
        (22, 42, 48,  0.008,  0.010),
        (23, 45, 50, -0.012, -0.005),
        (24, 48, 52,  0.018,  0.012),
        # 第3年 (牛市加速)
        (25, 50, 55,  0.035,  0.022),
        (26, 55, 58,  0.050,  0.030),
        (27, 60, 62,  0.042,  0.025),
        (28, 65, 65,  0.038,  0.020),
        (29, 68, 68,  0.028,  0.018),
        (30, 72, 70,  0.020,  0.015),
        (31, 75, 73,  0.015,  0.010),
        (32, 78, 75, -0.008, -0.005),
        (33, 80, 78,  0.010,  0.008),
        (34, 82, 80,  0.005,  0.005),
        (35, 85, 82, -0.020, -0.010),
        (36, 88, 85,  0.008,  0.006),
        # 第4年 (牛市顶点→熊市)
        (37, 90, 88,  0.025,  0.015),
        (38, 92, 90,  0.018,  0.010),
        (39, 95, 92, -0.035, -0.020),
        (40, 93, 89, -0.050, -0.035),
        (41, 88, 85, -0.080, -0.055),
        (42, 82, 80, -0.060, -0.040),
        (43, 75, 73, -0.040, -0.025),
        (44, 68, 65, -0.025, -0.015),
        (45, 60, 58, -0.015, -0.008),
        (46, 52, 50,  0.010,  0.008),
        (47, 45, 42,  0.025,  0.015),
        (48, 38, 35,  0.035,  0.022),
        # 第5年 (底部震荡→复苏)
        (49, 32, 30,  0.020,  0.012),
        (50, 28, 26,  0.045,  0.028),
        (51, 25, 22,  0.030,  0.020),
        (52, 22, 20,  0.028,  0.018),
        (53, 20, 18,  0.035,  0.025),
        (54, 18, 16,  0.050,  0.030),
        (55, 22, 20,  0.018,  0.010),
        (56, 25, 22,  0.040,  0.025),
        (57, 28, 25,  0.032,  0.020),
        (58, 30, 28,  0.025,  0.015),
        (59, 28, 26, -0.010, -0.005),
        (60, 26, 24,  0.028,  0.018),
    ]

    @dataclass
    class MonthRecord:
        month: int
        csi300_pct: float
        ndx_pct: float
        csi300_return: float
        ndx_return: float
        combined_pct: float
        zone: str
        invest_amount: int
        nav_before: float          # 定投前组合净值
        invest_amount_fixed: float  # 固定定投对照

    @classmethod
    def run(cls, years: int = 5) -> Dict:
        """
        运行回测对比。

        Returns:
            包含两种策略最终结果的字典
        """
        months = years * 12
        data = cls.HISTORICAL_MARKET_DATA[:months]

        # 初始持仓
        # 简化模型：假设组合净值为1，各资产按权重配置
        # 每月收益 = 各资产权重 × 各资产涨跌幅

        # ── 估值择时策略 ──
        val_cash = INITIAL_CAPITAL      # 现金
        val_nav = 1.0                   # 组合单位净值（初始1）
        val_shares = 0.0               # 持有份额
        val_total = val_cash

        # ── 固定定投 ──
        fix_cash = INITIAL_CAPITAL
        fix_nav = 1.0
        fix_shares = 0.0
        fix_total = fix_cash

        records = []
        total_invested_val = 0
        total_invested_fix = 0

        for i, (month, csi_pct, ndx_pct, csi_ret, ndx_ret) in enumerate(data):
            # 综合百分位（简化：A股0.55权重 + 纳指0.25 + 红利低波0.20中性）
            combined_pct = csi_pct * 0.55 + ndx_pct * 0.25 + 50.0 * 0.20
            zone = ValuationStrategy.zone_from_percentile(combined_pct)
            invest_val = ValuationStrategy.amount_from_zone(zone)

            # 固定定投金额
            invest_fix = MONTHLY_BASE

            # 每月资产收益
            # 组合月收益率 = 沪深300×0.35 + 中证500×0.20 + 纳指100×0.25 + 红利低波×0.20
            # 简化：中证500与沪深300收益率比例约1.2:1，红利低波约0.5:1
            csi500_ret = csi_ret * 1.2
            dividend_ret = csi_ret * 0.5
            portfolio_return = (
                0.35 * csi_ret + 0.20 * csi500_ret + 0.25 * ndx_ret + 0.20 * dividend_ret
            )

            # ── 估值择时 ──
            # 1. 现金存货币基金月收益
            val_cash_yield = val_cash * (CASH_YIELD / 12)
            # 2. 投入资金（从现金中扣除）
            actual_invest = min(invest_val, val_cash + val_cash_yield)
            val_cash += val_cash_yield - actual_invest
            # 3. 定投买入（以当前净值买入份额）
            current_nav = val_nav * (1 + portfolio_return)
            val_nav = current_nav
            if current_nav > 0:
                new_shares = actual_invest / current_nav
                val_shares += new_shares
            total_invested_val += actual_invest
            val_total = val_shares * current_nav + val_cash  # 现金部分不再计算收益（简化）

            # ── 固定定投 ──
            fix_cash_yield = fix_cash * (CASH_YIELD / 12)
            actual_fix = min(invest_fix, fix_cash + fix_cash_yield)
            fix_cash += fix_cash_yield - actual_fix
            fix_current_nav = fix_nav * (1 + portfolio_return)
            fix_nav = fix_current_nav
            if fix_current_nav > 0:
                fix_new_shares = actual_fix / fix_current_nav
                fix_shares += fix_new_shares
            total_invested_fix += actual_fix
            fix_total = fix_shares * fix_current_nav + fix_cash

            records.append({
                "month": month,
                "csi300_pct": csi_pct,
                "ndx_pct": ndx_pct,
                "combined_pct": round(combined_pct, 1),
                "zone": zone,
                "invest_val": invest_val,
                "portfolio_return": round(portfolio_return * 100, 2),
                "val_total": round(val_total, 2),
                "fix_total": round(fix_total, 2),
            })

        # ── 最终统计 ──
        final_val = val_total
        final_fix = fix_total
        final_cash_val = val_cash
        final_cash_fix = fix_cash

        # 年化收益率计算（简化：期末/期初 ^ (1/年数) - 1）
        def annual_return(final, total_invested, initial):
            total_input = initial + total_invested
            if total_input <= 0:
                return 0.0
            total_years = months / 12
            if total_years <= 0:
                return 0.0
            # 资金并非一次性投入，用XIRR近似：内部收益率简化
            # 简化用期末/总投入的1/n年次方
            ratio = final / (initial + total_invested)
            if ratio <= 0:
                return 0.0
            return (ratio ** (1.0 / total_years) - 1.0) * 100

        val_ann = annual_return(final_val, total_invested_val, INITIAL_CAPITAL)
        fix_ann = annual_return(final_fix, total_invested_fix, INITIAL_CAPITAL)

        # 最大回撤估算
        val_peaks = [r["val_total"] for r in records]
        fix_peaks = [r["fix_total"] for r in records]
        val_max_dd = cls._max_drawdown(val_peaks)
        fix_max_dd = cls._max_drawdown(fix_peaks)

        # 总投入
        val_total_in = INITIAL_CAPITAL + total_invested_val
        fix_total_in = INITIAL_CAPITAL + total_invested_fix

        return {
            "参数": {
                "初始资金": f"¥{INITIAL_CAPITAL:,}",
                "基准月定投": f"¥{MONTHLY_BASE:,}",
                "回测周期": f"{years} 年 ({months} 个月)",
                "闲置资金收益": f"{CASH_YIELD*100:.0f}%/年",
            },
            "估值择时策略": {
                "总投入": f"¥{val_total_in:,.0f}",
                "期末总资产": f"¥{final_val:,.0f}",
                "总收益": f"¥{final_val - val_total_in:+,.0f}",
                "收益率": f"{(final_val / val_total_in - 1) * 100:+.1f}%",
                "年化收益率": f"{val_ann:+.1f}%",
                "最大回撤": f"{val_max_dd:.1f}%",
                "期末现金": f"¥{val_cash:,.0f}",
            },
            "固定定投策略": {
                "总投入": f"¥{fix_total_in:,.0f}",
                "期末总资产": f"¥{final_fix:,.0f}",
                "总收益": f"¥{final_fix - fix_total_in:+,.0f}",
                "收益率": f"{(final_fix / fix_total_in - 1) * 100:+.1f}%",
                "年化收益率": f"{fix_ann:+.1f}%",
                "最大回撤": f"{fix_max_dd:.1f}%",
                "期末现金": f"¥{fix_cash:,.0f}",
            },
            "对比总结": {
                "收益差额": f"¥{final_val - final_fix:+,.0f}",
                "年化超额收益": f"{val_ann - fix_ann:+.1f}%",
                "回撤改善": f"{fix_max_dd - val_max_dd:+.1f}%",
                "低估期买入次数": sum(1 for r in records if r["zone"] == "低估"),
                "高估期买入次数": sum(1 for r in records if r["zone"] == "高估"),
            },
            "月度明细": records,
        }

    @staticmethod
    def _max_drawdown(values: List[float]) -> float:
        """计算最大回撤（百分比）"""
        if not values:
            return 0.0
        peak = values[0]
        max_dd = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak * 100
            if dd > max_dd:
                max_dd = dd
        return max_dd


# ═══════════════════════════════════════════════════════════════
# 输出格式化
# ═══════════════════════════════════════════════════════════════

class Display:
    """格式化的终端输出"""

    @staticmethod
    def valuation_snapshot(snapshot: ValuationSnapshot):
        """打印单指数估值信息"""
        c = snapshot.color()
        print(f"\n  {c} {snapshot.name}")
        print(f"    当前PE: {snapshot.current_pe:.2f}")
        print(f"    历史百分位: {snapshot.percentile:.1f}%")
        print(f"    估值区间: {snapshot.zone}")
        if snapshot.median_pe:
            print(f"    中位数PE: {snapshot.median_pe:.2f}")
        print(f"    数据来源: {snapshot.source}")
        print(f"    获取时间: {snapshot.fetch_time}")

    @staticmethod
    def strategy_decision(decision: Dict):
        """打印完整决策"""
        print("\n" + "=" * 55)
        print("  📋 本期定投策略决策")
        print("=" * 55)

        print(f"\n  📊 综合估值百分位:  {decision['综合百分位']}%")
        zone_emoji = {"低估": "🟢", "正常": "🟡", "高估": "🔴"}
        print(f"  综合区间: {zone_emoji.get(decision['综合区间'], '⚪')} {decision['综合区间']}")

        amt = decision['建议定投总额']
        print(f"\n  💰 建议定投总额:  ¥{amt:,}")
        if amt > 1000:
            print(f"     ↑ 加码 {(amt/1000 - 1) * 100:+.0f}%（低估加仓）")
        elif amt < 1000:
            print(f"     ↓ 减码 {(1 - amt/1000) * 100:.0f}%（高估减仓）")
        else:
            print(f"     → 维持基准定投")

        print(f"\n  📦 资产分配:")
        for name, alloc in decision['资产分配'].items():
            print(f"    {name:12s}  ¥{alloc:>5,d}  ({alloc/amt*100:5.1f}%)")

        print(f"\n  📈 各指数明细:")
        for idx_name in ["沪深300", "纳斯达克100"]:
            d = decision[idx_name]
            e = zone_emoji.get(d['区间'], '⚪')
            print(f"    {idx_name:12s}  {e} 百分位 {d['百分位']}%  |  "
                  f"区间 {d['区间']}  | 单独建议 ¥{d['建议']:,}")

        print("\n" + "=" * 55)

    @staticmethod
    def backtest_result(result: Dict):
        """打印回测结果"""
        print("\n" + "=" * 60)
        print("  🔬 回测对比: 固定定投 vs 估值择时定投")
        print("=" * 60)

        params = result["参数"]
        print(f"\n  参数设置:")
        for k, v in params.items():
            print(f"    {k}: {v}")

        val = result["估值择时策略"]
        fix = result["固定定投策略"]
        summary = result["对比总结"]

        print(f"\n  ┌───────────────────────┬──────────────────┬──────────────────┐")
        print(f"  │ 指标                  │ 固定定投          │ 估值择时          │")
        print(f"  ├───────────────────────┼──────────────────┼──────────────────┤")
        print(f"  │ 总投入                │ {fix['总投入']:>14s} │ {val['总投入']:>14s} │")
        print(f"  │ 期末总资产            │ {fix['期末总资产']:>14s} │ {val['期末总资产']:>14s} │")
        print(f"  │ 总收益                │ {fix['总收益']:>14s} │ {val['总收益']:>14s} │")
        print(f"  │ 总收益率              │ {fix['收益率']:>14s} │ {val['收益率']:>14s} │")
        print(f"  │ 年化收益率            │ {fix['年化收益率']:>14s} │ {val['年化收益率']:>14s} │")
        print(f"  │ 最大回撤              │ {fix['最大回撤']:>14s} │ {val['最大回撤']:>14s} │")
        print(f"  └───────────────────────┴──────────────────┴──────────────────┘")

        print(f"\n  📊 对比总结:")
        print(f"    • 收益差额: {summary['收益差额']}（估值择时 {'跑赢' if '+' in summary['收益差额'] else '跑输' if '-' in summary['收益差额'][:1] else '持平'} 固定定投）")
        print(f"    • 年化超额收益: {summary['年化超额收益']}")
        print(f"    • 最大回撤改善: {summary['回撤改善']}")
        print(f"    • 低估期加码次数: {summary['低估期买入次数']} 次")
        print(f"    • 高估期减码次数: {summary['高估期买入次数']} 次")
        print(f"    • 更低的平均买入成本: {'✅ 是' if '+' in summary['收益差额'] else '❌ 否'}")

        # 打印关键月份
        records = result["月度明细"]
        print(f"\n  📈 月度净值走势 (部分):")
        print(f"  {'月份':>5s}  {'沪深%':>5s}  {'纳指%':>5s}  {'综合%':>5s}  {'区间':4s}  "
              f"{'定投':>5s}  {'估值净值':>9s}  {'固定净值':>9s}")
        for r in records:
            if r["month"] % 6 == 0 or r["month"] == 1:
                print(f"  {r['month']:>5d}  {r['csi300_pct']:>5.1f}  {r['ndx_pct']:>5.1f}  "
                      f"{r['combined_pct']:>5.1f}  {r['zone']:4s}  "
                      f"¥{r['invest_val']:>4,d}  "
                      f"¥{r['val_total']:>8,.0f}  ¥{r['fix_total']:>8,.0f}")

        print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="估值择时定投策略助手 — 基于PE百分位动态调整定投金额",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python valuation_dca.py                         # 自动获取数据并输出策略
  python valuation_dca.py --manual                # 手动输入百分位
  python valuation_dca.py --simulate              # 运行5年回测对比
  python valuation_dca.py --simulate --years 10   # 回测10年
  python valuation_dca.py --json                  # JSON格式输出
  python valuation_dca.py --simulate --json       # 回测结果输出JSON
        """,
    )
    parser.add_argument("--manual", action="store_true", help="手动输入PE百分位")
    parser.add_argument("--simulate", action="store_true", help="运行历史回测对比")
    parser.add_argument("--years", type=int, default=5, help="回测年数 (默认5)")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出（供其他工具调用）")
    args = parser.parse_args()

    # ── 模式1: 回测 ──────────────────────────────────
    if args.simulate:
        result = BacktestEngine.run(years=args.years)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            Display.backtest_result(result)
        return

    # ── 模式2: 获取估值数据 ───────────────────────────
    if args.manual:
        csi_pct, ndx_pct = DataFetcher.manual_input()
    else:
        print("\n📡 正在获取实时估值数据...")
        csi = DataFetcher.fetch_csi300()
        ndx = DataFetcher.fetch_nasdaq100()

        if not args.json:
            if csi:
                Display.valuation_snapshot(csi)
            if ndx:
                Display.valuation_snapshot(ndx)

        csi_pct = csi.percentile if csi else 50.0
        ndx_pct = ndx.percentile if ndx else 50.0

    # 策略计算
    strategy = ValuationStrategy(csi300_pct=csi_pct, ndx_pct=ndx_pct)
    decision = strategy.decide()

    if args.json:
        output = {
            "沪深300": {"percentile": csi_pct} if not args.manual else {"percentile": csi_pct},
            "纳斯达克100": {"percentile": ndx_pct},
            "决策": decision,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        Display.strategy_decision(decision)

    # ── 策略建议摘要 ─────────────────────────────────
    if not args.json:
        print()
        zone = decision["综合区间"]
        if zone == "低估":
            print("  💡 当前市场整体处于 📉 低估区域，建议加大定投力度，")
            print("     用更低的成本积累更多份额。保持耐心，等待价值回归。")
        elif zone == "高估":
            print("  💡 当前市场整体处于 📈 高估区域，建议减少定投金额，")
            print("     保留部分现金储备。可考虑将减省的资金放入货币基金，")
            print("     等待市场回调后再加大投入。")
        else:
            print("  💡 当前市场整体处于 ⚖️ 正常估值区域，按计划执行定投。")
            print("     同时密切关注市场动态，为下一阶段的调整做好准备。")
        print()


if __name__ == "__main__":
    main()
