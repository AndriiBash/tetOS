# ==============================================================================
# main.py
# ==============================================================================
# Author:      AndriiBash
# Created:     2025-12-21
# Project:     TetOS (github.com/AndriiBash/tetOS)
# ==============================================================================


import os
import sys
import subprocess
import threading
import platform
import config
import server_commands

from pathlib import Path
from config import (
    GREEN,
    YELLOW,
    RED,
    CYAN,
    RESET,
    VERSION
    )

try:
    from telegram_bot import (
        init_bot, 
        )
    config.TELEGRAM_LIB_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import telegram_bot.py: {e}")
    config.TELEGRAM_LIB_AVAILABLE = False


# ===== Основная CLI петля =====
server_commands.clear_terminal()
banner = f"""{RED}
      _____          _      {RESET}___    ____  {RED}
     |_   _|   ___  | |_   {RESET}/ _ \  / ___| {RED}
       | |    / _ \ | __| {RESET}| | | | \___ \ {RED}
       | |   |  __/ | |_  {RESET}| |_| |  ___) |{RED}
       |_|    \___|  \__|  {RESET}\___/  |____/ {RESET}
   """

bot_success = False
if config.TELEGRAM_LIB_AVAILABLE:
    bot_success = init_bot()

info_line = f"Version: {YELLOW}{VERSION}{RESET}"

if not config.TELEGRAM_BOT_RUNNING:
    tg_color = RED
    tg_available = "not available"
else:
    tg_color = GREEN
    tg_available = "available"

if config.TELEGRAM_BOT_NOTIFICATION:
    tg_color_available = GREEN
    tg_status = "(on)"
else:
    tg_color_available = RED
    tg_status = "(off)"

status_line = f"Telegram notifications: {tg_color}{tg_available} {tg_color_available}{tg_status}{RESET}"

max_len = max(len(info_line), len(status_line)) - 6
print(banner)
print(f"┌{'─' * (max_len - 3)}┐")
print(f"│  {info_line.center(max_len)}    │")
print(f"│  {status_line.center(max_len)}   │")
print(f"└{'─' * (max_len - 3)}┘\n")

if not config.TELEGRAM_LIB_AVAILABLE:
    print(f"{RED}🔕 Telegram notifications disabled (missing telegram_bot.py or libraries){RESET}")


# Получаем и задаем макс значения игроков и памяти
config.SERVER_MAX_PLAYERS = server_commands.get_max_players()
config.SERVER_MAX_RAM_MB = server_commands.get_max_ram_mb()


try:
    while True:
        cmd_input = input().strip()
        parts = cmd_input.split()
        cmd = parts[0]
        args = parts[1:]

        # Команды утилиты 
        if cmd == "info":
            server_commands.print_server_info()

        elif cmd in ["tetos", "version"]:
            print(f"Utility version: {YELLOW}{VERSION}{RESET}")

        elif cmd == "start":
            hard_mode = "--hard" in args
            server_commands.start_server(hard=hard_mode)

        elif cmd == "exit":
            server_commands.exit_utility()

        elif cmd == "clear" or cmd == "cls":
            server_commands.clear_terminal()

        elif cmd == "stop":
            server_commands.stop_server()

        elif cmd == "restart":
            server_commands.restart_server()
        
        elif cmd == "tps":
            server_commands.print_tps_info("tps")

        elif cmd == "mspt":
            server_commands.print_tps_info("mspt")

        elif cmd == "get-ip":
            server_commands.print_ip_server()

        elif cmd == "set":
            server_commands.handle_set_command(args)

        elif cmd == "help":
            server_commands.print_help_server()

        else:
            if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
                config.SERVER_PROCESS.stdin.write(cmd_input + "\n")
                config.SERVER_PROCESS.stdin.flush()
            else:
                print(f"{YELLOW}Server is not running! Use 'start' to launch.{RESET}")

except KeyboardInterrupt:
    print(f"\n{RED}✋ All be okay...{RESET}")
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        config.SERVER_PROCESS.stdin.write("stop\n")
        config.SERVER_PROCESS.stdin.flush()
        config.SERVER_PROCESS.wait()
    sys.exit(0)

