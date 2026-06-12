#!/usr/bin/env python3
"""淘宝联盟 CDP - 获取推广链接（修复版）"""
import json, time, urllib.request, sys, os

CDP = "http://127.0.0.1:9222"

def load_creds():
    cred_path = os.path.expanduser("~/nexus-knowledge/zhihu-pipeline/.taobao-credentials")
    creds = {}
    with open(cred_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            k, v = line.split(":", 1)
            creds[k.strip()] = v.strip()
    return creds

creds = load_creds()
print(f"账号: {creds['username']}, MID: {creds['mid']}")

from websocket import create_connection
vdata = json.loads(urllib.request.urlopen(f"{CDP}/json/version").read())
ws = create_connection(vdata['webSocketDebuggerUrl'])
msg_id = 0

def cmd(method, params=None, session=None):
    global msg_id
    msg_id += 1
    payload = {"id": msg_id, "method": method, "params": params or {}}
    if session: payload["sessionId"] = session
    ws.send(json.dumps(payload))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == msg_id: return r

def new_page(url):
    r = cmd("Target.createTarget", {"url": url})
    tid = r['result']['targetId']
    time.sleep(5)
    r2 = cmd("Target.attachToTarget", {"targetId": tid, "flatten": True})
    sid = r2['result']['sessionId']
    cmd("Runtime.enable", session=sid)
    cmd("Page.enable", session=sid)
    return tid, sid

def eval_js(js, sid):
    r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True}, session=sid)
    try: return r['result']['result']['value']
    except: return r

def navigate(url, sid):
    """Use Page.navigate for proper cookie handling"""
    r = cmd("Page.navigate", {"url": url}, session=sid)
    # Wait for load
    time.sleep(5)
    return r

# Open alimama
print("打开淘宝联盟首页...")
tid, sid = new_page("https://pub.alimama.com/")
url = eval_js("location.href", sid)
print(f"当前URL: {url}")

if "login" in url.lower():
    print("需要登录...")
    # Navigate to login page directly
    navigate("https://login.taobao.com/member/login.jhtml?redirectURL=https://pub.alimama.com/", sid)
    time.sleep(3)
    
    # Switch to password mode
    eval_js("""
    (function(){
        var el = document.querySelector('[data-spm="passwordlogin"]');
        if (el) el.click();
    })()
    """, sid)
    time.sleep(2)
    
    # Fill form
    eval_js(f"""
    (function(){{
        var u = document.querySelector('input[name="fm-login-id"]');
        var p = document.querySelector('input[name="fm-login-password"]');
        if (u) u.value = {json.dumps(creds['username'])};
        if (p) p.value = {json.dumps(creds['password'])};
        if (u) {{
            u.dispatchEvent(new Event('input', {{bubbles: true}}));
            u.dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
        if (p) {{
            p.dispatchEvent(new Event('input', {{bubbles: true}}));
            p.dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
        return 'filled';
    }})()
    """, sid)
    time.sleep(0.5)
    
    # Click login
    eval_js("""
    (function(){
        var btn = document.querySelector('button[type="submit"]') || document.querySelector('.fm-button');
        if (btn) btn.click();
        return 'clicked';
    })()
    """, sid)
    time.sleep(5)
    print(f"登录后URL: {eval_js('location.href', sid)}")

# Now go to search
mid = creds['mid']
products = [
    ("天堂晴雨伞三折", "天堂伞 三折晴雨伞防晒"),
    ("蕉下果趣系列", "蕉下果趣晴雨伞 双层"),
    ("网易严选超轻遮阳伞", "网易严选 超轻遮阳伞 210g"),
]

for name, keyword in products:
    print(f"\n{'='*40}")
    print(f"搜索: {keyword}")
    search_url = f"https://pub.alimama.com/items/search.htm?q={urllib.request.quote(keyword)}"
    navigate(search_url, sid)
    
    url = eval_js("location.href", sid)
    print(f"URL: {url}")
    
    # Check if we got redirected to login
    if "login" in url.lower():
        print("⚠️ 搜索页需要重新登录")
        continue
    
    # Extract product info
    info = eval_js("""
    (function(){
        var text = document.body ? document.body.innerText : '';
        return text.substring(0, 1500);
    })()
    """, sid)
    print(f"页面内容:\n{info}")

ws.close()
print("\n=== 完成 ===")
