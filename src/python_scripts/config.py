# ==============================================================================
# config.py
# ==============================================================================
# Author:      AndriiBash
# Created:     2025-12-22
# Project:     TetOS (github.com/AndriiBash/tetOS)
# ==============================================================================


import os
import sys
import platform

from pathlib import Path


# ===== Конфиги TetOS =====
VERSION = "2026.1.22"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SERVER_DIR = PROJECT_ROOT / "server"
RUN_SCRIPT = PROJECT_ROOT / "src" / "run_server.sh"
ENV_PATH = PROJECT_ROOT / ".env"
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
SERVER_IP = "0"
SERVER_LOCAL_IP = "0"
SERVER_PORT = "0"


# ===== Настройки для Minecraft =====
AVAILABLE_GAME_MODES = [
    "survival",
    "creative",
    "adventure",
    "spectator",
]

AVAILABLE_DIFFICULTIES = [
    "peaceful",
    "easy",
    "normal",
    "hard",
]
