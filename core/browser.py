import os, sys
import subprocess
import traceback
from playwright.sync_api import sync_playwright
from utils.config import DEBUG, get_environment, Environment

PLAYWRIGHT_BROWSERS_PATH = "../chrome"

def install_browser():
    """
    安装 Chromium 浏览器
    """
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("浏览器安装完成，请重新运行程序。")
    except subprocess.CalledProcessError as e:
        print(f"发生未知错误：{e}")


def get_browser():
    """
    启动浏览器实例
    :return: 浏览器实例
    """

    headless = True

    env = get_environment()
    if env == Environment.LOCAL:
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.abspath(
            os.path.join(os.path.dirname(__file__), PLAYWRIGHT_BROWSERS_PATH)
        )
        if DEBUG:
            headless = False
    elif env == Environment.PACKED:
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.abspath(
            os.path.join(os.path.dirname(sys.executable), PLAYWRIGHT_BROWSERS_PATH)
        )

    try:
        # [加固 2026-09-18] channel/headless 可用环境变量覆盖：
        # 国内网络常拉不到 playwright CDN 的 chromium，设 CHROME_CHANNEL=chrome
        # 可直接用本机已装的 Google Chrome；CHROME_HEADLESS=1 强制无头（覆盖 DEBUG 的可视化模式）。
        channel = os.getenv("CHROME_CHANNEL", "").strip()
        headless_env = os.getenv("CHROME_HEADLESS", "").strip().lower()
        if headless_env:
            headless = headless_env not in ("0", "false", "no")
        # 启动浏览器
        playwright = sync_playwright().start()
        launch_kwargs = {"headless": headless}
        if channel:
            launch_kwargs["channel"] = channel
        browser = playwright.chromium.launch(**launch_kwargs)
        return playwright, browser
    except Exception as e:
        # 捕获浏览器启动错误
        if "Executable doesn't exist" in str(e) and env != Environment.GITHUBACTION:
            print("浏览器可执行文件不存在！")
            install_browser()
            sys.exit(1)
        else:
            traceback.print_exc()
