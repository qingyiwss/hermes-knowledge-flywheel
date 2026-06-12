#!/usr/bin/env python3
"""知乎内容自动生成器 — 产品评测 / 清单 / 问答 三类模板"""

import json, os, sys
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/nexus-knowledge/zhihu-pipeline")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PRODUCT_REVIEW_TEMPLATE = """# {title}

> 本文为真实体验分享，文末有购买链接，通过链接下单作者可获得小额佣金（不影响你的价格）。

## 先说结论

{conclusion}

## 我为什么买了它

{buy_reason}

## 使用体验（{days}天真实感受）

### 优点
{pros}

### 缺点
{cons}

## 和竞品对比

{comparison}

## 适合谁买？

{target_user}

## 总结

{final_verdict}

---

{affiliate_links}

*以上链接均来自淘宝联盟，价格与官网一致。*
"""

LIST_TEMPLATE = """# {title}

> 整理了{count}款高性价比的{category}，预算{price_range}元以内。文末有购买链接。

{intro}

## {count}款{category}推荐

{items}

## 选购建议

{advice}

## 常见问题

{faq}

---

{affiliate_links}

*通过以上链接购买，作者可获得小额佣金。*
"""

QA_TEMPLATE = """# {question}

{short_answer}

{detailed_body}

{summary}

---

{affiliate_links}
"""

def generate_product_review(topic, search_results=""):
    """生成产品评测类文章"""
    from datetime import date
    return {
        "type": "review",
        "title": topic["title"],
        "category": topic["category"],
        "template": PRODUCT_REVIEW_TEMPLATE,
        "placeholders": {
            "title": topic["title"],
            "conclusion": "[需填写：一句话结论]",
            "buy_reason": "[需填写：购买原因]",
            "days": "30",
            "pros": "[需填写：优点列表]",
            "cons": "[需填写：缺点]",
            "comparison": "[需填写：竞品对比]",
            "target_user": "[需填写：目标用户]",
            "final_verdict": "[需填写：最终建议]",
            "affiliate_links": "[需填写：淘宝客链接]",
        }
    }

def generate_list_article(topic):
    """生成清单类文章"""
    count = 5 if "推荐" in topic["title"] else 3
    return {
        "type": "list",
        "title": topic["title"],
        "category": topic["category"],
        "template": LIST_TEMPLATE,
        "placeholders": {
            "title": topic["title"],
            "count": str(count),
            "category": topic["product"],
            "price_range": "50-500",
            "intro": f"花了不少时间筛选了{count}款好用的{topic['product']}，每一款都亲自用过或做了充分调研。",
            "items": f"[需填写：{count}款产品详情，每款包含名称/价格/推荐理由]",
            "advice": "[需填写：根据预算和需求的选购建议]",
            "faq": "[需填写：常见问题Q&A]",
            "affiliate_links": "[需填写：淘宝客链接]",
        }
    }

def generate_qa(topic):
    """生成问答类文章"""
    return {
        "type": "qa",
        "title": topic["title"],
        "template": QA_TEMPLATE,
        "placeholders": {
            "question": topic["title"],
            "short_answer": "[需填写：简短回答]",
            "detailed_body": "[需填写：详细分析]",
            "summary": "[需填写：总结]",
            "affiliate_links": "[需填写：淘宝客链接]",
        }
    }

if __name__ == "__main__":
    # 测试：加载今日选题
    today = datetime.now().strftime("%Y-%m-%d")
    topics_path = os.path.join(OUTPUT_DIR, f"topics-{today}.json")
    
    if os.path.exists(topics_path):
        with open(topics_path) as f:
            data = json.load(f)
        
        # 生成一篇样文
        evergreen = [t for t in data["topics"] if t["type"] == "evergreen"]
        if evergreen:
            # 按佣金率降序选TOP1
            topic = max(evergreen, key=lambda t: float(t["commission_pct"].rstrip("%")))
            article = generate_list_article(topic) if "推荐" in topic["title"] else generate_product_review(topic)
            
            output_path = os.path.join(OUTPUT_DIR, "latest-article.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(article, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已生成: {article['title'][:40]}")
            print(f"   类型: {article['type']}")
            print(f"   模板: {article['template'][:80]}...")
            print(f"   保存至: {output_path}")
    else:
        print("❌ 今日选题不存在，请先运行 topic-research.py")
