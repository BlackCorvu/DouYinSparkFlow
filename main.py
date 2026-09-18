# 尝试从 .env 文件加载环境变量
import os
if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")

import sys

from core.tasks import runTasks

# [加固 2026-09-18] 失败时退出码非零：cron / GitHub Actions 才能感知真实失败，不再假成功
if not runTasks():
    sys.exit(1)
