# ==============================================================================
# server_commands.py
# ==============================================================================
# Author:      AndriiBash
# Created:     2025-12-28
# Project:     TetOS (github.com/AndriiBash/tetOS)
# ==============================================================================

import os
import sys
import subprocess
import threading
import platform
import config

from typing import Optional
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
        broadcast,
        notify_server_ready,
        notify_server_stopped,
        notify_server_restarted
    )
except ImportError:
    print(f"Failed to import telegram_bot.py (notification) in server_commands.py: {e}")
    broadcast = lambda *_: None
    notify_server_ready = lambda: None
    notify_server_stopped = lambda: None
    notify_server_restarted = lambda: None


# ===== Убиваем процесс, который использует порт =====
def kill_process_on_port(port=25565) -> bool:
    import subprocess
    try:
        result = subprocess.run(
            ["lsof", "-t", f"-i:{port}"],
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().split("\n")
        if not pids or pids == ['']:
            # Если на порту никого нет
            return False
        for pid in pids:
            if pid:
                subprocess.run(["kill", "-9", pid])
                print(f"{RED}🔪 Killed process {pid} on port {port}{RESET}")
        return True
    except Exception as e:
        print(f"{RED}❌ Failed to kill process on port {port}: {e}{RESET}")
        return False


# ===== Функция для получения порта из server.properties =====
def get_server_port(default_port=25565) -> int:
    props_file = config.SERVER_DIR.parent / "server.properties"
    if not props_file.exists():
        return default_port
    try:
        with open(props_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("server-port="):
                    return int(line.strip().split("=")[1])
    except Exception:
        pass
    return default_port


# ===== Функция для запуска сервера =====
def start_server(hard: bool = False):
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{YELLOW}Server is already running!{RESET}")
        return

    if hard:
        print(f"{RED}🚨 Server HARD start ...{RESET}")
        port = get_server_port()
        kill_process_on_port(port)
    else:
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
def stop_server(silent: bool = False):
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{RED}🛑 Stopping server...{RESET}")
        config.SERVER_PROCESS.stdin.write("stop\n")
        config.SERVER_PROCESS.stdin.flush()
        config.SERVER_PROCESS.wait()
        config.SERVER_PROCESS = None
        config.SERVER_IS_READY = False
        config.SERVER_GAME_MODE = "UNKNOWN"
        config.SERVER_MC_VERSION = "UNKNOWN"
        config.SERVER_IP = "Unknown"
        config.SERVER_LOCAL_IP = "Unknown"
        config.SERVER_PORT = "Unknown"

        print(f"{RED}🛑 Server stopped!{RESET}")

        if silent is False:
            notify_server_stopped()
    else:
        print(f"{YELLOW}Server is not running! Use 'start' to launch.{RESET}")


# ===== Функция для перезапуска сервера =====
def restart_server():
    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{YELLOW}🔄 Restarting server...{RESET}")
        stop_server(silent=True)
        start_server()
        notify_server_restarted()

        config.SERVER_ONLINE_PLAYERS = 0
    else:
        start_server()


# ===== Функция для чтения max-players из server.properties =====
def get_max_players():
    props_file = config.SERVER_DIR / "server.properties"
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


# ===== Функция для чтения максимальной RAM из run_server.sh =====
def get_max_ram_mb():
    script_file = config.RUN_SCRIPT
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


# ===== Функция для получения IP Hamachi =====
def detect_hamachi_ip() -> str:
    try:
        ip = subprocess.check_output(
            "hamachi | awk -F': +' '/address/ {print $2}' | awk '{print $1}'",
            shell=True,
            text=True
        ).strip()
        return ip if ip else "Unknown"
    except Exception:
        return "Unknown"


# ===== Функция для получения IP Local =====
def get_local_ip() -> str:
    try:
        ip = subprocess.check_output(
            ["ipconfig", "getifaddr", "en0"],
            text=True
        ).strip()
        return ip if ip else "Unknown"
    except Exception:
        return "Unknown"


# ===== Функция для расчёта размера мира =====
def get_world_size():
    world_dir = config.SERVER_DIR / "world"
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


# ===== Функция для окраски TPS =====
def colorize_tps(tps: float) -> str:
    if tps >= 18.0:
        return GREEN
    elif tps >= 12.0:
        return YELLOW
    else:
        return RED


# ===== Функция для окраски MSPT =====
def colorize_mspt(mspt: float) -> str:
    if mspt <= 50.0:
        return GREEN
    elif mspt <= 75.0:
        return YELLOW
    else:
        return RED


# ===== Функция для расчёта TPS и MSPT (только возвращает значения) =====
def fetch_tps():
    if config.SERVER_PROCESS is None or config.SERVER_PROCESS.poll() is not None:
        return 0.0, 0.0

    import re

    # Отправляем команду серверу
    config.SERVER_PROCESS.stdin.write("tick query\n")
    config.SERVER_PROCESS.stdin.flush()

    tps = 0.0
    mspt = 0.0

    # Читаем несколько строк ответа
    for _ in range(15):  # максимум 15 строк
        line = config.SERVER_PROCESS.stdout.readline()
        if not line:
            continue
        if "Average time per tick:" in line:
            match = re.search(r"Average time per tick: ([\d\.]+)ms", line)
            if match:
                mspt = float(match.group(1))
                tps = min(20.0, 1000.0 / mspt)
            break

    return tps, mspt


# ===== Функция для парсинга ввода команды set для RAM(min, max) =====
def parse_ram_value(value: str) -> Optional[int]:
    value = value.strip().upper()
    try:
        if value.endswith(("GB", "G")):
            return int(value.rstrip("GB").rstrip("G")), "G"
        if value.endswith(("MB", "M")):
            return int(value.rstrip("MB").rstrip("M")), "M"
        # если без суффикса — считаем как GB
        return int(value), "G"
    except ValueError:
        return None


# ===== Функция для обновления значения RAM сервера =====
def update_run_script_ram(run_script: config.RUN_SCRIPT, ram_min_mb=None, ram_max_mb=None, ram_min_unit="M", ram_max_unit="M"):
    if not run_script.exists():
        print(f"{RED}run_server.sh not found!{RESET}")
        return False

    content = run_script.read_text()
    import re

    match = re.search(r"exec java .*", content)
    if not match:
        print(f"{RED}Cannot find java exec line in run_server.sh{RESET}")
        return False

    old_line = match.group(0)
    new_line = old_line

    # Обновляем min RAM
    if ram_min_mb is not None:
        new_line = re.sub(r"-Xms\S+", f"-Xms{ram_min_mb}{ram_min_unit}", new_line)

    # Обновляем max RA
    if ram_max_mb is not None:
        new_line = re.sub(r"-Xmx\S+", f"-Xmx{ram_max_mb}{ram_max_unit}", new_line)

    content = content.replace(old_line, new_line)
    run_script.write_text(content)

    # Выводим в одну строку
    parts = []
    if ram_min_mb is not None:
        parts.append(f"min: {ram_min_mb}{ram_min_unit}")
    if ram_max_mb is not None:
        parts.append(f"max: {ram_max_mb}{ram_max_unit}")

    print(f"{GREEN}Updated RAM in run_server.sh: {'; '.join(parts)}{RESET}")

    return True


# ===== Функция для получения значения min/max RAM из run_server.sh  =====
def get_current_ram_value(which="min"):
    content = config.RUN_SCRIPT.read_text()
    import re
    if which == "min":
        match = re.search(r"-Xms(\d+[MG])", content, re.IGNORECASE)
    else:
        match = re.search(r"-Xmx(\d+[MG])", content, re.IGNORECASE)
    if match:
        val = match.group(1).upper()
        number = int(val[:-1])
        unit = val[-1]
        return number, unit
    return None, None


# ===== Функция для обработки команды set =====
def handle_set_command(args: list):
    gamemodes = "|".join(config.AVAILABLE_GAME_MODES)
    difficulties = "|".join(config.AVAILABLE_DIFFICULTIES)

    if len(args) != 2:
        print(f"{YELLOW}Usage: set <option> <value>{RESET}")
        print("Options:")
        print(f"  max-players  {CYAN}<1-999>{RESET}         - Set the maximum count of players on the server")
        print(f"  motd         {CYAN}<text>{RESET}          - Set the server MOTD (message of the day/server name)")
        print(f"  gamemode     {CYAN}<{gamemodes}>{RESET}   - Set default game mode")
        print(f"  difficulty   {CYAN}<{difficulties}>{RESET}- Set server difficulty")
        print(f"  ram-min      {CYAN}<GB|MB>{RESET}         - Set minimum RAM (e.g., 1G, 1024M)")
        print(f"  ram-max      {CYAN}<GB|MB>{RESET}         - Set maximum RAM (e.g., 4G, 4096M)")
        print(f"  notify       {CYAN}<on|off>{RESET}        - Enable/disable Telegram notifications")
        print(f"  tocken       {CYAN}<your:tocken>{RESET}   - For work Telegram notifications")
        print(f"\nExamples: {CYAN}set gamemode creative{RESET}, {CYAN}set ram-max 4G{RESET}")
        return 

    if config.SERVER_PROCESS is not None and config.SERVER_PROCESS.poll() is None:
        print(f"{RED}❌ Cannot change settings while the server is running! Stop the server first, use 'stop'.{RESET}")
        return

    option = args[0].lower()
    value = ' '.join(args[1:])

    # ===== Проверка валидности и обработка =====
    if option == "max-players":
        try:
            val = int(value)
            if 1 <= val <= 999:
                update_server_property("max-players", str(val))
                config.SERVER_MAX_PLAYERS = val
            else:
                print(f"{RED}❌ Value must be between 1 and 999{RESET}")
        except ValueError:
            print(f"{RED}❌ Invalid number: {value}{RESET}")
    
    elif option == "motd":
        update_server_property("motd", value)

    elif option == "gamemode":
        if value.lower() in config.AVAILABLE_GAME_MODES:
            update_server_property("gamemode", value.lower())
            config.SERVER_GAME_MODE = value.lower()
        else:
            print(f"{RED}❌ Invalid gamemode. Choose: {gamemodes}{RESET}")

    elif option == "difficulty":
        if value.lower() in config.AVAILABLE_DIFFICULTIES:
            update_server_property("difficulty", value.lower())
            config.SERVER_GAME_MODE = value.lower()
        else:
            print(f"{RED}❌ Invalid difficulty. Choose: {difficulties}{RESET}")

    elif option == "ram-min":
        parsed = parse_ram_value(value)
        if parsed is None:
            print(f"{RED}Invalid RAM value{RESET}")
            return
        ram_value, ram_unit = parsed

        current_max_value, current_max_unit = get_current_ram_value("max")
        if current_max_value is not None:
            # Конвертируем в МБ для сравнения
            ram_min_mb = ram_value * (1024 if ram_unit.upper() == "G" else 1)
            ram_max_mb = current_max_value * (1024 if current_max_unit.upper() == "G" else 1)
            if ram_min_mb > ram_max_mb:
                print(f"{RED}❌ Cannot set min RAM greater than current max RAM ({current_max_value}{current_max_unit}){RESET}")
                return

        update_run_script_ram(config.RUN_SCRIPT, ram_min_mb=ram_value, ram_min_unit=ram_unit)

    elif option == "ram-max":
        parsed = parse_ram_value(value)
        if parsed is None:
            print(f"{RED}Invalid RAM value{RESET}")
            return
        ram_value, ram_unit = parsed

        # Берём текущий min из run_server.sh
        current_min_value, current_min_unit = get_current_ram_value("min")
        if current_min_value is not None:
            ram_min_mb = current_min_value * (1024 if current_min_unit.upper() == "G" else 1)
            ram_max_mb = ram_value * (1024 if ram_unit.upper() == "G" else 1)
            if ram_max_mb < ram_min_mb:
                print(f"{RED}❌ Cannot set max RAM smaller than current min RAM ({current_min_value}{current_min_unit}){RESET}")
                return

        update_run_script_ram(config.RUN_SCRIPT, ram_max_mb=ram_value, ram_max_unit=ram_unit)

    elif option == "notify":
        # W.I.P
        print("notify")
    
    else:
        print(f"{RED}❌ Unknown option: {option}{RESET}")


# ===== Функция обновления server.properties =====
def update_server_property(option: str, value: str):
    props_file = config.SERVER_DIR / "server.properties"
    if not props_file.exists():
        print(f"{RED}server.properties not found at {props_file}{RESET}")
        return False

    updated = False
    lines = []
    with open(props_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith(option + "="):
                lines.append(f"{option}={value}\n")
                updated = True
            else:
                lines.append(line)

    if not updated:
        # если ключ не найден, добавляем его в конец
        lines.append(f"{option}={value}\n")

    try:
        with open(props_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"{GREEN}Updated server property: {option}={value}{RESET}")
        return True
    except Exception as e:
        print(f"{RED}Failed to write server.properties: {e}{RESET}")
        return False


# ===== Команда для вывода IP сервера =====
def print_ip_server():
    if config.SERVER_PROCESS is None or config.SERVER_PROCESS.poll() is not None:
        print(f"{YELLOW}Server is not running! Use 'start' to launch.{RESET}")
        return

    print(f"🌐 IP (Hamachi): {config.SERVER_IP}:{config.SERVER_PORT}")
    print(f"📡 IP (Local): {config.SERVER_LOCAL_IP}:{config.SERVER_PORT}")        


# ===== Команда для получения и вывода TPS и MSPT =====
def print_tps_info(mode="all"):
    if config.SERVER_PROCESS is None or config.SERVER_PROCESS.poll() is not None:
        print(f"{YELLOW}Server is not running! Use 'start' to launch.{RESET}")
        return

    tps, mspt = fetch_tps()
    tps_color = colorize_tps(tps)
    mspt_color = colorize_mspt(mspt)

    if mode == "tps":
        print(f"⚡ TPS: {tps_color}{tps:.2f}{RESET}")
    elif mode == "mspt":
        print(f"🕓 MSPT: {mspt_color}{mspt:.2f} ms{RESET}")
    else:
        print(f"⚡ TPS: {tps_color}{tps:.2f}{RESET} | 🕓 MSPT: {mspt_color}{mspt:.2f} ms{RESET}")


# ===== Выводим основную информацию про сервер в терминал =====
def print_server_info():
    print(f"📋 Server Info:")

    config.SERVER_MAX_PLAYERS = get_max_players()
    config.SERVER_MAX_RAM_MB = get_max_ram_mb()

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
                            config.SERVER_LOCAL_IP = get_local_ip()
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

