import os
import sys
import platform

from pathlib import Path


# ===== Конфиги =====
VERSION = "2025.12.23"
SERVER_DIR = Path(__file__).resolve().parent
RUN_SCRIPT = SERVER_DIR.parent / "run_server.sh"
OS_NAME = platform.system()
if OS_NAME in ["Linux", "Darwin"]:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
else:
    GREEN = YELLOW = RED = CYAN = RESET = ""


# ==== Telgram work's ====
TELEGRAM_BOT = None
TELEGRAM_BOT_THREAD = None
TELEGRAM_BOT_RUNNING = False
TELEGRAM_USERS_FILE = Path(__file__).resolve().parent.parent / "telegram_cache" / "tg_users.txt"
TELEGRAM_USERS_FILE.parent.mkdir(parents=True, exist_ok=True)


# ===== Состояние сервера =====
SERVER_IS_READY = False
SERVER_GAME_MODE = "UNKNOWN"
SERVER_MC_VERSION = "UNKNOWN"
SERVER_PROCESS = None
SERVER_ONLINE_PLAYERS = 0
SERVER_MAX_PLAYERS = 1
SERVER_MAX_RAM_MB = 2048
