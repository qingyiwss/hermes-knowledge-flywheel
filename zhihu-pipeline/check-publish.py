#!/usr/bin/env python3
"""检查知乎发布结果"""
import json, time, urllib.request

from websocket import create_connection
CDP = "http://127.0.0.1:9222"
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

# Navigate to the article page
r = cmd("Target.createTarget", {"url": "https://zhuanlan.zhihu.com/p/2045928608275994214"})
tid = r['result']['targetId']
time.sleep(5)
r2 = cmd("Target.attachToTarget", {"targetId": tid, "flatten": True})
sid = r2['result']['sessionId']
cmd("Runtime.enable", session=sid)

def ev(js):
    r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True}, session=sid)
    try: return r['result']['result']['value']
    except: return r

title = ev("document.title")
url = ev("location.href")
body = ev("document.querySelector('article') ? document.querySelector('article').innerText.substring(0, 200) : 'no article'")

print(f"标题: {title}")
print(f"URL: {url}")
print(f"正文预览: {body}")

# Also check the edit tab status
for t in json.loads(urllib.request.urlopen(f"{CDP}/json").read()):
    if 'zhuanlan.zhihu.com' in t.get('url', ''):
        print(f"标签: {t['url'][:80]}")

ws.close()
