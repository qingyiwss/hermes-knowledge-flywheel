#!/usr/bin/env python3
"""发布知乎草稿 - 已有 tab 直接点击发布"""
import json, time, urllib.request

CDP = "http://127.0.0.1:9222"

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

# Get the zhihu tab
tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
target_id = None
for t in tabs:
    if 'zhuanlan.zhihu.com' in t.get('url', '') and 'edit' in t.get('url', ''):
        target_id = t['id']
        print(f"找到标签: {t['url']}")
        break

if not target_id:
    print("❌ 未找到知乎编辑标签")
    ws.close()
    exit(1)

# Attach
r = cmd("Target.attachToTarget", {"targetId": target_id, "flatten": True})
sid = r['result']['sessionId']
cmd("Runtime.enable", session=sid)

def ev(js):
    r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True}, session=sid)
    try: return r['result']['result']['value']
    except: return r

time.sleep(2)

# 检查状态
state = ev("""
(function(){
    var e = document.querySelector('[contenteditable="true"]');
    var ta = document.querySelector('textarea');
    var pub = '?';
    document.querySelectorAll('button').forEach(function(b){
        if (b.innerText && b.innerText.indexOf('发布') > -1) {
            pub = b.innerText + ':' + (!b.disabled ? 'ON' : 'OFF') + ' class:' + b.className;
        }
    });
    return JSON.stringify({
        bodyLen: e ? e.innerText.length : 0,
        titleLen: ta ? ta.value.length : 0,
        title: ta ? ta.value.substring(0, 40) : '?',
        publish: pub
    });
})()
""")
print(f"状态: {state}")

# 点击发布
print("点击发布按钮...")
ev("""
(function(){
    document.querySelectorAll('button').forEach(function(b){
        if (b.innerText && b.innerText.indexOf('发布') > -1 && !b.disabled) {
            b.click();
        }
    });
    return 'done';
})()
""")

time.sleep(5)

# 确认结果
result = ev("location.href + ' | ' + document.title")
print(f"发布后: {result}")

ws.close()
