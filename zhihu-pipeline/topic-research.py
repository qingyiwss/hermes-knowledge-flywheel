#!/usr/bin/env python3
"""知乎内容选题引擎 — 多数据源聚合，每日生成选题清单"""

import json, os, sys
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/nexus-knowledge/zhihu-pipeline")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 高佣类目（淘宝联盟 2026 佣金率）
HIGH_COMMISSION = {
    "美妆个护": 0.15, "母婴用品": 0.10, "食品饮料": 0.12,
    "数码家电": 0.05, "图书文娱": 0.05, "家居家装": 0.08,
    "服饰鞋包": 0.10, "运动户外": 0.08, "日用百货": 0.10,
}

# 常青选题模板（无需实时数据也能写）
EVERGREEN_TEMPLATES = [
    {"title": "2026年{品类}推荐清单（预算{价格}以内）", "category": "数码家电"},
    {"title": "用了{品类}半年，说几句大实话", "category": "数码家电"},
    {"title": "{品类}怎么选？看完这篇就够了", "category": "家居家装"},
    {"title": "避坑指南：这些{品类}千万别买", "category": "日用百货"},
    {"title": "学生党{品类}推荐，性价比炸裂", "category": "数码家电"},
    {"title": "{品类}评测：哪款最值得入手？", "category": "美妆个护"},
    {"title": "上班族必备{品类}清单", "category": "运动户外"},
    {"title": "母婴用品红黑榜：这些{品类}真的好用", "category": "母婴用品"},
]

def fetch_baidu_hot():
    """抓取百度热搜"""
    import urllib.request, re
    try:
        req = urllib.request.Request(
            "https://top.baidu.com/board?tab=realtime",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req, timeout=10).read().decode()
        items = re.findall(r'<div class="c-single-text-ellipsis">(.*?)</div>', html)
        return items[:15]
    except:
        return []

def generate_topics():
    """生成今日选题"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 百度热搜
    baidu_hot = fetch_baidu_hot()
    
    # 匹配高佣类目
    topics = []
    
    # 1. 常青选题 × 高佣类目
    import random
    for template in random.sample(EVERGREEN_TEMPLATES, 5):
        cat = template["category"]
        commission = HIGH_COMMISSION.get(cat, 0.05)
        # 具体品类
        products = {
            "数码家电": ["蓝牙耳机", "充电宝", "机械键盘", "显示器", "路由器"],
            "美妆个护": ["防晒霜", "洗面奶", "面膜", "精华液", "口红"],
            "家居家装": ["人体工学椅", "台灯", "收纳盒", "乳胶枕", "窗帘"],
            "母婴用品": ["婴儿推车", "奶瓶", "纸尿裤", "辅食机", "安全座椅"],
            "运动户外": ["跑鞋", "瑜伽垫", "筋膜枪", "运动手环", "泳镜"],
            "日用百货": ["保温杯", "雨伞", "拖鞋", "毛巾", "垃圾桶"],
        }
        product = random.choice(products.get(cat, ["好物"]))
        title = template["title"].replace("{品类}", product).replace("{价格}", random.choice(["200", "500", "1000"]))
        topics.append({
            "title": title,
            "category": cat,
            "commission_pct": f"{commission*100:.0f}%",
            "type": "evergreen",
            "product": product,
        })
    
    # 2. 蹭热点
    for hot in baidu_hot[:5]:
        topics.append({
            "title": f"关于「{hot}」，普通人怎么看？",
            "category": "热点",
            "commission_pct": "N/A",
            "type": "hotspot",
        })
    
    # 保存
    output = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "baidu_hot_count": len(baidu_hot),
        "topics": topics,
    }
    
    path = os.path.join(OUTPUT_DIR, f"topics-{today}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 打印
    print(f"📅 {today} 选题清单 ({len(topics)} 个)")
    print(f"   百度热搜: {len(baidu_hot)} 条")
    print()
    for i, t in enumerate(topics):
        badge = "🔥" if t["type"] == "hotspot" else "📝"
        print(f"  {badge} [{t['category']}] {t['title']}")
        if t["type"] == "evergreen":
            print(f"      佣金: {t['commission_pct']} | 品类: {t['product']}")
    
    return output

if __name__ == "__main__":
    generate_topics()
