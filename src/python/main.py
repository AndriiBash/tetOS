import os
import sys
import subprocess
import threading
import platform

from pathlib import Path


# ===== Конфиги =====
VERSION = "2025.12.22"
SERVER_DIR = Path(__file__).resolve().parent
RUN_SCRIPT = SERVER_DIR / "run_server.sh"
OS_NAME = platform.system()
if OS_NAME in ["Linux", "Darwin"]:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
else:
    GREEN = YELLOW = RED = CYAN = RESET = ""


# ===== Состояние сервера =====
SERVER_IS_READY = False
SERVER_GAME_MODE = "UNKNOWN"
SERVER_MC_VERSION = "UNKNOWN"
SERVER_PROCESS = None
SERVER_ONLINE_PLAYERS = 0
SERVER_MAX_PLAYERS = 20 #need fix, get info from server.prop


# ===== Функция для расчёта размера мира =====
def get_world_size():
    world_dir = SERVER_DIR / "world"
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
    if SERVER_PROCESS is None or SERVER_PROCESS.poll() is not None:
        return "0 MB"
    try:
        import psutil
        p = psutil.Process(SERVER_PROCESS.pid)
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
    global SERVER_PROCESS
    if SERVER_PROCESS is not None and SERVER_PROCESS.poll() is None:
        print(f"{RED}🛑 Stopping server before exiting...{RESET}")
        SERVER_PROCESS.stdin.write("stop\n")
        SERVER_PROCESS.stdin.flush()
        SERVER_PROCESS.wait()
    clear_terminal()
    sys.exit(0)


# ===== Функция для чтения логов сервера =====
def read_output(process):
    global SERVER_IS_READY, SERVER_GAME_MODE, SERVER_MC_VERSION, SERVER_ONLINE_PLAYERS
    try:
        for line in iter(process.stdout.readline, ''):
            if line:  # Проверяем, что строка не пустая
                sys.stdout.write(line)
                sys.stdout.flush()

                if "Default game type:" in line:
                    SERVER_GAME_MODE = line.split("Default game type:")[1].strip()
                if "Starting minecraft server version" in line:
                    SERVER_MC_VERSION = line.split("Starting minecraft server version")[1].strip()
                if "Done (" in line and not SERVER_IS_READY:
                    SERVER_IS_READY = True
                    print(f"{GREEN}✅ Server is ready!{RESET}")
                if "joined the game" in line:
                    SERVER_ONLINE_PLAYERS += 1
                if "left the game" in line:
                    SERVER_ONLINE_PLAYERS = max(0, SERVER_ONLINE_PLAYERS - 1)
    except ValueError:
        pass


# ===== Функция для запуска сервера =====
def start_server():
    global SERVER_PROCESS, SERVER_IS_READY
    if SERVER_PROCESS is not None and SERVER_PROCESS.poll() is None:
        print(f"{YELLOW}⚡ Server is already running!{RESET}")
        return

    print(f"{GREEN}🚀 Starting server...{RESET}")
    SERVER_IS_READY = False
    SERVER_GAME_MODE = "UNKNOWN"
    SERVER_MC_VERSION = "UNKNOWN"

    SERVER_PROCESS = subprocess.Popen(
        [str(RUN_SCRIPT)],
        cwd=SERVER_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    threading.Thread(target=read_output, args=(SERVER_PROCESS,), daemon=True).start()


# ===== Основная CLI петля =====
clear_terminal()
print(f"""{RED}
  _____          _      ___    ____  
 |_   _|   ___  | |_   / _ \  / ___| 
   | |    / _ \ | __| | | | | \___ \ 
   | |   |  __/ | |_  | |_| |  ___) |
   |_|    \___|  \__|  \___/  |____/ {RESET}
          version: {YELLOW}{VERSION}{RESET}                       
          """)

try:
    while True:
        cmd = input().strip().lower()

        # ---- Кастомные команды утилиты ----
        if cmd == "pingme":
            print(f"{YELLOW}🏓 PONG!{RESET}")

        elif cmd == "info":
            print(f"📋 Server Info:")
            if SERVER_PROCESS is None or SERVER_PROCESS.poll() is not None:
                print(f" - Status: {RED}Not running{RESET}")
                print(f" - Minecraft version: {YELLOW}Unknown{RESET}")
                print(f" - Game mode: {YELLOW}Unknown{RESET}")
                print(f" - Online players: {YELLOW}0/{SERVER_MAX_PLAYERS}{RESET}")
                print(f" - Used RAM: {YELLOW}0 MB{RESET}")
                print(f" - World size: {YELLOW}Unknown{RESET}")
            else:
                status = f"{GREEN}Running (ready){RESET}" if SERVER_IS_READY else f"{YELLOW}Running (starting...){RESET}"
                print(f" - Status: {status}")
                print(f" - Minecraft version: {YELLOW}{SERVER_MC_VERSION}{RESET}")
                print(f" - Game mode: {YELLOW}{SERVER_GAME_MODE}{RESET}")
                print(f" - Online players: {GREEN}{SERVER_ONLINE_PLAYERS}/{SERVER_MAX_PLAYERS}{RESET}")
                print(f" - Used RAM: {YELLOW}{get_used_ram()}{RESET}")
                print(f" - World size: {YELLOW}{get_world_size()}{RESET}")

        elif cmd in ["tetos", "version"]:
            print(f"Utility version: {YELLOW}{VERSION}{RESET}")

        elif cmd == "start":
            start_server()

        elif cmd == "exit":
            exit_utility()

        elif cmd == "stop":
            if SERVER_PROCESS is not None and SERVER_PROCESS.poll() is None:
                print(f"{RED}🛑 Stopping server...{RESET}")
                SERVER_PROCESS.stdin.write("stop\n")
                SERVER_PROCESS.stdin.flush()
                SERVER_PROCESS.wait()
                SERVER_PROCESS = None
                SERVER_IS_READY = False
                SERVER_GAME_MODE = "UNKNOWN"
                SERVER_MC_VERSION = "UNKNOWN"
            else:
                print(f"{YELLOW}⚠ Server is not running!{RESET}")

        elif cmd == "restart":
            if SERVER_PROCESS is not None and SERVER_PROCESS.poll() is None:
                print(f"{YELLOW}🔄 Restarting server...{RESET}")
                SERVER_PROCESS.stdin.write("stop\n")
                SERVER_PROCESS.stdin.flush()
                SERVER_PROCESS.wait()
                SERVER_PROCESS = None
                SERVER_IS_READY = False
                SERVER_GAME_MODE = "UNKNOWN"
                SERVER_MC_VERSION = "UNKNOWN"
            start_server()

        else:
            if SERVER_PROCESS is not None and SERVER_PROCESS.poll() is None:
                SERVER_PROCESS.stdin.write(cmd + "\n")
                SERVER_PROCESS.stdin.flush()
            else:
                print(f"{YELLOW}Server is not running! Use 'start' to launch.{RESET}")

except KeyboardInterrupt:
    print(f"\n{RED}✋ All be okay...{RESET}")
    if SERVER_PROCESS is not None and SERVER_PROCESS.poll() is None:
        SERVER_PROCESS.stdin.write("stop\n")
        SERVER_PROCESS.stdin.flush()
        SERVER_PROCESS.wait()
    sys.exit(0)