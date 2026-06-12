#!/usr/bin/env python3
"""知乎发布 v3 - 两阶段发布：点发布 → 弹设置窗 → 确认发布"""
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

def ev(js, sid):
    r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True}, session=sid)
    try: return r['result']['result']['value']
    except: return r

# Find edit tab
tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
target_id = None
for t in tabs:
    if 'zhuanlan.zhihu.com' in t.get('url', '') and 'edit' in t.get('url', ''):
        target_id = t['id']
        break

if not target_id:
    print("❌ 无知乎编辑标签")
    exit(1)

r = cmd("Target.attachToTarget", {"targetId": target_id, "flatten": True})
sid = r['result']['sessionId']
cmd("Runtime.enable", session=sid)
cmd("Page.enable", session=sid)

# 刷新页面清状态
print("刷新页面...")
cmd("Page.reload", {}, session=sid)
time.sleep(5)

# 等一下确保页面完全加载
ev("""
(function(){
    // 等待编辑器加载
    return document.querySelector('[contenteditable="true"]') ? 'editor_ready' : 'waiting';
})()
""", sid)
time.sleep(3)

# 验证内容还在
state = ev("""
(function(){
    var e = document.querySelector('[contenteditable="true"]');
    return JSON.stringify({
        ready: !!e,
        bodyLen: e ? e.innerText.length : 0
    });
})()
""", sid)
print(f"刷新后: {state}")

# 如果内容丢失需要重新注入
if '"bodyLen":0' in state or '"ready":false' in state:
    print("内容丢失，需要重新注入")
    # Read article
    import os
    with open(os.path.expanduser("~/nexus-knowledge/zhihu-pipeline/article-2026-06-04.md")) as f:
        md = f.read()
    lines = md.split('\n')
    title = lines[0].replace('# ', '').strip()
    import re
    body_lines = []
    for l in lines[2:]:
        l = re.sub(r'\*\*(.+?)\*\*', r'\1', l.strip())
        l = re.sub(r'^###?\s+', '', l)
        body_lines.append(l)
    body = '\n'.join(body_lines)
    
    # Inject body
    print(f"注入正文 ({len(body)} chars)...")
    ev(f"""
    (function(){{
        var ed = document.querySelector('[contenteditable="true"]');
        var fiberKey = Object.keys(ed).find(k => k.startsWith('__reactFiber'));
        var fiber = ed[fiberKey];
        while (fiber) {{
            if (fiber.memoizedState && fiber.memoizedState.editorState && fiber.stateNode) {{
                fiber.stateNode.resetWithValue({json.dumps(body)});
                break;
            }}
            fiber = fiber.return;
        }}
        return 'ok';
    }})()
    """, sid)
    time.sleep(1)
    
    # Inject title
    print(f"注入标题: {title}")
    ev(f"""
    (function(){{
        var ta = document.querySelector('textarea');
        var f = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
        f.call(ta, {json.dumps(title)});
        ta.dispatchEvent(new Event('input', {{bubbles: true}}));
        ta.dispatchEvent(new Event('change', {{bubbles: true}}));
        ta.blur();
        return ta.value.length;
    }})()
    """, sid)
    time.sleep(1)
    
    # Second title fix
    ev(f"""
    (function(){{
        var ta = document.querySelector('textarea');
        var f = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
        f.call(ta, {json.dumps(title)});
        ta.focus(); ta.blur();
        return 'fixed:' + ta.value.length;
    }})()
    """, sid)
    time.sleep(1)
    print("✅ 重新注入完成")

# === STEP 1: Click publish button to open settings panel ===
print("\n=== 第1步：点击发布按钮 ===")
pub_click = ev("""
(function(){
    var buttons = document.querySelectorAll('button');
    var found = false;
    buttons.forEach(function(b){
        var t = b.innerText || '';
        if (t.indexOf('发布') > -1 && t.indexOf('中') === -1 && !b.disabled) {
            b.click();
            found = true;
        }
    });
    return found ? 'clicked' : 'not_found';
})()
""", sid)
print(f"点击结果: {pub_click}")

# Wait for settings panel
time.sleep(3)

# Check what appeared
panel_info = ev("""
(function(){
    // Look for settings panel/modal
    var panels = document.querySelectorAll('[class*="Modal"], [class*="modal"], [class*="Setting"], [class*="setting"], [class*="Publish"], [class*="publish"]');
    var r = [];
    panels.forEach(function(p) {
        r.push({
            class: p.className.substring(0, 60),
            visible: p.offsetParent !== null,
            buttons: Array.from(p.querySelectorAll('button')).map(function(b) {
                return b.innerText + (b.disabled ? '(disabled)' : '');
            })
        });
    });
    // Also look for any visible buttons with publish/confirm text
    var allBtns = [];
    document.querySelectorAll('button').forEach(function(b){
        if (b.offsetParent !== null) {
            var t = b.innerText || '';
            if (t.length > 0 && t.length < 20) allBtns.push(t);
        }
    });
    return JSON.stringify({panels: r, visibleButtons: allBtns});
})()
""", sid)
print(f"面板状态: {panel_info}")

# === STEP 2: Click confirm in settings panel ===
print("\n=== 第2步：确认发布 ===")
confirm_click = ev("""
(function(){
    document.querySelectorAll('button').forEach(function(b){
        if (b.offsetParent !== null) {
            var t = b.innerText || '';
            // Look for second publish/confirm button in the panel
            if ((t === '发布' || t.indexOf('确认') > -1 || t.indexOf('确定') > -1) && !b.disabled) {
                b.click();
                return 'clicked_confirm';
            }
        }
    });
    return 'no_confirm_button';
})()
""", sid)
print(f"确认结果: {confirm_click}")

time.sleep(5)

# Check if redirected
final = ev("location.href + ' | title=' + document.title", sid)
print(f"\n最终: {final}")

ws.close()
