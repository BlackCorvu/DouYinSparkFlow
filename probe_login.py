"""登录探针：只验证 cookies 是否还能进入聊天页，不发送任何消息。

用法：.venv/bin/python probe_login.py
退出码：0 = 登录有效；1 = 登录失效/异常
"""
import os
import sys
import time

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")

from utils.config import get_userData
from core.browser import get_browser


def main():
    users = get_userData()
    if not users:
        print("PROBE-FAIL: TASKS 未配置或 cookies 缺失")
        return 1
    user = users[0]
    playwright, browser = get_browser()
    page = None
    try:
        ctx = browser.new_context()
        ctx.set_default_timeout(30000)
        page = ctx.new_page()
        ctx.add_cookies(user["cookies"])
        page.goto("https://www.douyin.com/chat", wait_until="domcontentloaded")
        time.sleep(6)
        if "passport" in page.url or "/login" in page.url:
            print(f"PROBE-FAIL: 被重定向到登录页 {page.url}")
            return 1
        for sel in ('iframe[src*="passport"]', "text=扫码登录", "text=验证码登录"):
            try:
                if page.locator(sel).first.is_visible():
                    print(f"PROBE-FAIL: 检测到登录弹窗（{sel}），cookies 已失效")
                    page.screenshot(path="logs/probe_expired.png")
                    return 1
            except Exception:
                pass
        page.wait_for_selector(".conversationConversationItemwrapper", timeout=60000)
        print("PROBE-OK: 登录有效，会话列表加载正常")
        return 0
    except Exception as e:
        print(f"PROBE-FAIL: {e}")
        try:
            if page:
                page.screenshot(path="logs/probe_fail.png")
        except Exception:
            pass
        return 1
    finally:
        try:
            browser.close()
            playwright.stop()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
