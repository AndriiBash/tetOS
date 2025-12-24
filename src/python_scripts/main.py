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
        broadcast,
        notify_server_ready,
        notify_server_stopped,
        notify_server_restarted
        )
    config.TELEGRAM_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import telegram_bot.py: {e}")
    config.TELEGRAM_AVAILABLE = False
    #broadcast = lambda message: None  # заглушка, чтобы не падало при вызове


# ===== Функция для чтения max-players из server.properties =====
def get_max_players():
    props_file = config.SERVER_DIR.parent / "server.properties"
    if not props_file.exists():
        return 1
    try:
        with open(props_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("max-players="):
                    return int(line.split("=")[1].strip())
    except:
        pass
    return 1


# ===== Функция для получения IP Hamachi =====
def detect_hamachi_ip():
    try:
        ip = subprocess.check_output(
            "hamachi | awk -F': +' '/address/ {print $2}' | awk '{print $1}'",
            shell=True,
            text=True
        ).strip()
        return ip if ip else "Unknown"
    except Exception:
        return "Unknown"


# ===== Функция для чтения максимальной RAM из run_server.sh =====
def get_max_ram_mb():
    script_file = config.SERVER_DIR.parent / "run_server.sh"
    if not script_file.exists():
        return 4096  # дефолт, если файла нет
    try:
        with open(script_file, "r", encoding="utf-8") as f:
            content = f.read()
            import re
            match = re.search(r'-Xmx(\d+)([MG])', content)
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                if unit == 'G':
                    return value * 1024
                else:
                    return value
    except:
        pass
    return 4096  # fallback


# ===== Функция для расчёта размера мира =====
def get_world_size():
    world_dir = config.SERVER_DIR.parent / "world"
    if not world_dir.exists():
        return "Unknown"
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(world_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    if total_size > 1024 * 1024 * 1024:
        return f"{total_size / (1024**3):.2f} GB"
    else:
        return f"{total_size / (1024**2):.2f} MB"


# ===== Функция для used RAM =====
def get_used_ram():
    if config.SERVER_PROCESS is None or config.SERVER_PROCESS.poll() is not None:
        return "0 MB"
    try:
        import psutil
        p = psutil.Process(config.SERVER_PROCESS.pid)
        return f"{p.memory_info().rss / (1024**2):.2f} MB"
    except:
        return f"{CYAN}Unknown (install psutil for accurate){RESET}"


# ===== Команда для очистки терминала =====
def clear_terminal():
    if platform.system() in ["Linux", "Darwin"]:
        os.system("clear")
    elif platform.system() == "Windows":
        os.system("cls")


# ===== Функция выхода из утилиты =====
def exit_utility():
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{RED}🛑 Stopping server before exiting...{RESET}")
        stop_server()
    clear_terminal()
    sys.exit(0)


# ===== Функция для чтения логов сервера =====
def read_output(process):
    try:
        for line in iter(process.stdout.readline, ''):
            if line:  # Проверяем, что строка не пустая
                sys.stdout.write(line)
                sys.stdout.flush()

                if "Starting Minecraft server on" in line:
                    try:
                        address_part = line.split("on")[1].strip()
                        if ":" in address_part:
                            ip_part, port_part = address_part.split(":", 1)
                            detected_port = port_part.strip()
                            config.SERVER_PORT = detected_port
                            config.SERVER_IP = detect_hamachi_ip()
                    except Exception as e:
                        print(f"{RED}Failed to recognize address: {e}{RESET}")


                if "Default game type:" in line:
                    config.SERVER_GAME_MODE = line.split("Default game type:")[1].strip()
                if "Starting minecraft server version" in line:
                    config.SERVER_MC_VERSION = line.split("Starting minecraft server version")[1].strip()
                if "Done (" in line and not config.SERVER_IS_READY:
                    config.SERVER_IS_READY = True
                    notify_server_ready()
                    print(f"{GREEN}✅ Server is ready!{RESET}")
                if "joined the game" in line:
                    config.SERVER_ONLINE_PLAYERS += 1
                    username = line.split("joined the game")[0].split()[-1]
                    broadcast(f"🎮 {username} joined the game!")
                if "left the game" in line:
                    config.SERVER_ONLINE_PLAYERS = max(0, config.SERVER_ONLINE_PLAYERS - 1)
                    username = line.split("left the game")[0].split()[-1]
                    broadcast(f"🔚 {username} left the game!")
    except ValueError:
        pass


# ===== Функция для запуска сервера =====
def start_server():
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{YELLOW}Server is already running!{RESET}")
        return

    print(f"{GREEN}🚀 Starting server...{RESET}")
    config.SERVER_IS_READY = False
    config.SERVER_GAME_MODE = "UNKNOWN"
    config.SERVER_MC_VERSION = "UNKNOWN"
    config.SERVER_MAX_PLAYERS = get_max_players()
    config.SERVER_MAX_RAM_MB = get_max_ram_mb()

    config.SERVER_PROCESS = subprocess.Popen(
        [str(config.RUN_SCRIPT)],
        cwd=config.SERVER_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    threading.Thread(target=read_output, args=(config.SERVER_PROCESS,), daemon=True).start()
    

# ===== Функция для остановки сервера =====
def stop_server(suppress_notification: bool = False):
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{RED}🛑 Stopping server...{RESET}")
        config.SERVER_PROCESS.stdin.write("stop\n")
        config.SERVER_PROCESS.stdin.flush()
        config.SERVER_PROCESS.wait()
        config.SERVER_PROCESS = None
        config.SERVER_IS_READY = False
        config.SERVER_GAME_MODE = "UNKNOWN"
        config.SERVER_MC_VERSION = "UNKNOWN"
        print(f"{RED}🛑 Server stopped!{RESET}")

        if suppress_notification is False:
            notify_server_stopped()
    else:
        print(f"{YELLOW}Server is not running!{RESET}")


# ===== Функция для перезапуска сервера =====
def restart_server():
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{YELLOW}🔄 Restarting server...{RESET}")
        stop_server(suppress_notification=True)
        start_server()
        notify_server_restarted()

        config.SERVER_ONLINE_PLAYERS = 0
    else:
        start_server()

# ===== Основная CLI петля =====
# clear_terminal вызывается чтобы убрать уведомление про устаревший OpenSSL
# который не влияет на роботоспособность

clear_terminal()
banner = f"""{RED}
  _____          _      {RESET}___    ____  {RED}
 |_   _|   ___  | |_   {RESET}/ _ \  / ___| {RED}
   | |    / _ \ | __| {RESET}| | | | \___ \ {RED}
   | |   |  __/ | |_  {RESET}| |_| |  ___) |{RED}
   |_|    \___|  \__|  {RESET}\___/  |____/ {RESET}
   """

bot_success = False
if config.TELEGRAM_AVAILABLE:
    bot_success = init_bot()

bot_status = "true" if (config.TELEGRAM_AVAILABLE and bot_success) else "false" if config.TELEGRAM_AVAILABLE else "off"
bot_color = GREEN if (config.TELEGRAM_AVAILABLE and bot_success) else RED if config.TELEGRAM_AVAILABLE else YELLOW

info_line = f"Version: {YELLOW}{VERSION}{RESET}"
status_line = f"Telegram notifications: {bot_color}{bot_status}{RESET}"

max_len = max(len(info_line), len(status_line)) + 4
print(banner)
print(f"┌{'─' * (max_len - 5)}┐")
print(f"│  {info_line.center(max_len)}  │")
print(f"│  {status_line.center(max_len)}  │")
print(f"└{'─' * (max_len - 5)}┘\n")

if not config.TELEGRAM_AVAILABLE:
    print(f"{RED}🔕 Telegram notifications disabled (missing telegram_bot.py or libraries){RESET}")

try:
    while True:
        cmd = input().strip().lower()

        # Команды утилиты
        if cmd == "info":
            print(f"📋 Server Info:")

            if config.SERVER_PROCESS is None or config.SERVER_PROCESS.poll() is not None:
                print(f" - Status: {RED}Not running{RESET}")
                print(f" - Minecraft version: {YELLOW}Unknown{RESET}")
                print(f" - Game mode: {YELLOW}Unknown{RESET}")
                print(f" - Online players: {YELLOW}0 / {config.SERVER_MAX_PLAYERS}{RESET}")
                print(f" - Used RAM: {YELLOW}0 MB / {config.SERVER_MAX_RAM_MB} MB{RESET}")
                print(f" - World size: {YELLOW}Unknown{RESET}")
            else:
                status = f"{GREEN}Running (ready){RESET}" if config.SERVER_IS_READY else f"{YELLOW}Running (starting...){RESET}"
                print(f" - Status: {status}")
                print(f" - Minecraft version: {YELLOW}{config.SERVER_MC_VERSION}{RESET}")
                print(f" - Game mode: {YELLOW}{config.SERVER_GAME_MODE}{RESET}")
                print(f" - Online players: {GREEN}{config.SERVER_ONLINE_PLAYERS} / {config.SERVER_MAX_PLAYERS}{RESET}")
                print(f" - Used RAM: {YELLOW}{get_used_ram()} / {config.SERVER_MAX_RAM_MB} MB{RESET}")
                print(f" - World size: {YELLOW}{get_world_size()}{RESET}")

        elif cmd in ["tetos", "version"]:
            print(f"Utility version: {YELLOW}{VERSION}{RESET}")

        elif cmd == "start":
            start_server()

        elif cmd == "exit":
            exit_utility()

        elif cmd == "clear" or cmd == "cls":
            clear_terminal()

        elif cmd == "stop":
            stop_server()

        elif cmd == "restart":
            restart_server()

        else:
            if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
                config.SERVER_PROCESS.stdin.write(cmd + "\n")
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

