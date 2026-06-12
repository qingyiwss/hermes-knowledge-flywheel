#!/usr/bin/env python3
"""API publish: get article ID from CDP tab, call publish API"""
import json, time, urllib.request, os, re

os.environ['NO_PROXY'] = '127.0.0.1,localhost'
os.environ['no_proxy'] = '127.0.0.1,localhost'

from websocket import create_connection

vdata = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/version").read())
ws = create_connection(vdata['webSocketDebuggerUrl'])

mid = [0]
def send(method, params=None, sid=None):
    mid[0] += 1
    m = {"id": mid[0], "method": method, "params": params or {}}
    if sid is not None:
        m["sessionId"] = sid
    ws.send(json.dumps(m))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == mid[0]:
            return r

# Find zhihu tab
targets_r = send("Target.getTargets")
targets = targets_r['result']['targetInfos']
zhihu_tab = None
for t in targets:
    if 'zhuanlan.zhihu.com' in t.get('url', ''):
        zhihu_tab = t
        print(f"Found: {t['title'][:50]} | {t['url'][:80]}")
        break

if not zhihu_tab:
    print("ERROR: No zhihu tab")
    ws.close()
    exit(1)

tid = zhihu_tab['targetId']
r = send("Target.attachToTarget", {"targetId": tid, "flatten": True})
sid = r['result']['sessionId']
send("Runtime.enable", sid=sid)

# Get URL and extract article ID
get_js = "(function(){return window.location.href;})()"
for attempt in range(15):
    r = send("Runtime.evaluate", {"expression": get_js, "returnByValue": True}, sid=sid)
    url = r['result']['result']['value']
    aid_m = re.search(r'/p/(\d+)', url)
    if aid_m:
        aid = aid_m.group(1)
        print(f"Article ID: {aid} (attempt {attempt+1})")
        break
    print(f"  Wait... URL: {url[:60]}")
    time.sleep(2)
else:
    print("ERROR: No article ID after 30s")
    ws.close()
    exit(1)

# Publish via API
pub_js = f"""(async function(){{
    try {{
        let resp = await fetch('https://zhuanlan.zhihu.com/api/articles/{aid}/publish', {{
            method: 'PUT',
            credentials: 'include',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                title: document.querySelector('textarea')?.value || '',
                content: document.querySelector('[contenteditable="true"]')?.innerText || '',
                column: null,
                type: 'article',
                copyright_permission: 'need_review'
            }})
        }});
        let text = await resp.text();
        return JSON.stringify({{status: resp.status, ok: resp.ok, body: text.substring(0, 300)}});
    }} catch(e) {{
        return JSON.stringify({{error: e.message}});
    }}
}})()"""

r = send("Runtime.evaluate", {"expression": pub_js, "awaitPromise": True, "returnByValue": True}, sid=sid)
result = json.loads(r['result']['result']['value'])
print(f"Result: {json.dumps(result, ensure_ascii=False)}")

ws.close()

if result.get('status') == 200:
    print(f"\n✅ PUBLISHED: https://zhuanlan.zhihu.com/p/{aid}")
else:
    print(f"\n⚠️ Publish returned {result.get('status')}: {result.get('body','')[:200]}")
    print(f"   Article saved as draft: https://zhuanlan.zhihu.com/p/{aid}/edit")
