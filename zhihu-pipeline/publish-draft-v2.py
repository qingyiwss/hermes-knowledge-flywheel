#!/usr/bin/env python3
"""发布知乎草稿 v2 - 处理确认弹窗"""
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

tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
target_id = None
for t in tabs:
    if 'zhuanlan.zhihu.com' in t.get('url', '') and 'edit' in t.get('url', ''):
        target_id = t['id']
        break

r = cmd("Target.attachToTarget", {"targetId": target_id, "flatten": True})
sid = r['result']['sessionId']
cmd("Runtime.enable", session=sid)

def ev(js):
    r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True}, session=sid)
    try: return r['result']['result']['value']
    except: return r

# 检查所有按钮
btns = ev("""
(function(){
    var bs = document.querySelectorAll('button');
    var r = [];
    bs.forEach(function(b, i) {
        r.push(i + ':' + (b.innerText || '').substring(0,30) + ' disabled=' + b.disabled);
    });
    return JSON.stringify(r);
})()
""")
print(f"按钮: {btns}")

# 查找发布按钮并获取位置
pub_info = ev("""
(function(){
    var btn = null;
    document.querySelectorAll('button').forEach(function(b){
        if (b.innerText && b.innerText.indexOf('发布') > -1) btn = b;
    });
    if (!btn) return 'no_button';
    var rect = btn.getBoundingClientRect();
    return JSON.stringify({
        x: rect.left + rect.width/2,
        y: rect.top + rect.height/2,
        text: btn.innerText,
        disabled: btn.disabled
    });
})()
""")
print(f"发布按钮位置: {pub_info}")

# 获取 nodeId 用于点击
node_info = ev("""
(function(){
    document.querySelectorAll('button').forEach(function(b){
        if (b.innerText && b.innerText.indexOf('发布') > -1) {
            b.setAttribute('data-hermes-publish', 'true');
        }
    });
    return 'marked';
})()
""")
print(f"标记: {node_info}")

# 用 CDP DOM 获取 nodeId 并 dispatch click
doc = cmd("DOM.getDocument", {"depth": -1}, session=sid)
print(f"DOM root nodeId: {doc.get('result', {}).get('root', {}).get('nodeId', '?')}")

# Find publish button node
find = cmd("DOM.querySelector", {
    "nodeId": doc['result']['root']['nodeId'],
    "selector": 'button[data-hermes-publish="true"]'
}, session=sid)
print(f"查找按钮: {json.dumps(find.get('result', {}), default=str)}")

if find.get('result', {}).get('nodeId'):
    btn_node = find['result']['nodeId']
    # Get box model for coordinates
    box = cmd("DOM.getBoxModel", {"nodeId": btn_node}, session=sid)
    print(f"Box: {json.dumps(box.get('result', {}).get('model', {}).get('content', []), default=str)}")
    
    if box.get('result', {}).get('model'):
        content = box['result']['model']['content']
        x = (content[0] + content[2]) / 2
        y = (content[1] + content[5]) / 2
        
        # Click using Input.dispatchMouseEvent
        cmd("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1}, session=sid)
        cmd("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1}, session=sid)
        print(f"✅ 已点击 ({x:.0f}, {y:.0f})")
        
        time.sleep(3)
        
        # Check for dialogs
        dialogs = ev("""
        (function(){
            var modals = document.querySelectorAll('[class*="Modal"], [class*="modal"], [class*="dialog"], [class*="Dialog"], [role="dialog"]');
            var r = [];
            modals.forEach(function(m) {
                r.push({
                    visible: m.offsetParent !== null,
                    text: m.innerText ? m.innerText.substring(0, 100) : ''
                });
            });
            // Also check for any "确认" or "确定" buttons
            var confirms = [];
            document.querySelectorAll('button').forEach(function(b){
                var t = b.innerText || '';
                if (t.indexOf('确定') > -1 || t.indexOf('确认') > -1 || t.indexOf('发布') > -1) {
                    confirms.push(t + (b.offsetParent !== null ? ' visible' : ' hidden'));
                }
            });
            return JSON.stringify({modals: r, confirms: confirms, url: location.href});
        })()
        """)
        print(f"点击后状态: {dialogs}")
        
        # Check if there's a confirm button to click
        if '"确定"' in dialogs or '"确认"' in dialogs or '"发布"' in dialogs:
            print("尝试点击确认...")
            ev("""
            (function(){
                document.querySelectorAll('button').forEach(function(b){
                    var t = b.innerText || '';
                    if (t.indexOf('确定') > -1 || t.indexOf('确认') > -1 || t.indexOf('发布') > -1) {
                        if (b.offsetParent !== null) {
                            b.click();
                        }
                    }
                });
                return 'done';
            })()
            """)
            time.sleep(3)
            final = ev("location.href + ' | ' + document.title")
            print(f"最终: {final}")

# Final check
final_state = ev("location.href + ' | title=' + document.title")
print(f"\n最终状态: {final_state}")

ws.close()
