#!/usr/bin/env python3
"""淘宝联盟自动登录 + 推广链接生成"""
from playwright.sync_api import sync_playwright
import time, sys, os

CDP_PORT = 9222
ALIMAMA = "https://pub.alimama.com/"

def connect():
    p = sync_playwright().start()
    browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
    return p, browser

def goto_alimama(page):
    page.goto(ALIMAMA, timeout=30000)
    time.sleep(3)
    # Check if already logged in
    if "login" not in page.url and "member/login" not in page.url:
        return "logged_in"
    return "need_login"

def login_with_password(username, password):
    """密码登录淘宝联盟"""
    p, browser = connect()
    page = browser.contexts[0].new_page()
    state = goto_alimama(page)
    
    if state == "logged_in":
        print("✅ 已登录")
        page.close()
        browser.close()
        p.stop()
        return
    
    # Find login iframe
    iframe = page.query_selector("iframe")
    frame = iframe.content_frame()
    
    # Switch to password mode
    pw_tab = frame.query_selector("text=密码登录")
    if pw_tab:
        pw_tab.click()
        time.sleep(1)
    
    # Fill credentials
    user_input = frame.query_selector('input[name="fm-login-id"], input[name="loginId"]')
    pass_input = frame.query_selector('input[name="fm-login-password"], input[name="password2"]')
    
    if user_input and pass_input:
        user_input.fill(username)
        pass_input.fill(password)
        time.sleep(0.5)
        
        # Click login
        submit = frame.query_selector('button[type="submit"], .fm-button')
        if submit:
            submit.click()
            time.sleep(3)
            print(f"登录后 URL: {page.url}")
    
    page.close()
    browser.close()
    p.stop()

def generate_link(keyword):
    """搜索商品并生成推广链接"""
    p, browser = connect()
    page = browser.contexts[0].new_page()
    
    # Go to product search
    page.goto("https://pub.alimama.com/items/search.htm", timeout=30000)
    time.sleep(3)
    
    # Search
    search_input = page.query_selector('input[placeholder*="搜索"], input[name="q"]')
    if search_input:
        search_input.fill(keyword)
        search_input.press("Enter")
        time.sleep(3)
    
    # Get page content
    text = page.evaluate("document.body.innerText")
    print(f"搜索结果:\n{text[:2000]}")
    
    page.close()
    browser.close()
    p.stop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 alimama-bot.py login <手机号> <密码>")
        print("      python3 alimama-bot.py search <关键词>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "login":
        login_with_password(sys.argv[2], sys.argv[3])
    elif cmd == "search":
        generate_link(sys.argv[2])
