# ==============================================================================
# telegram_bot.py
# ==============================================================================
# Author:      AndriiBash
# Created:     2025-12-22
# Project:     TetOS (github.com/AndriiBash/tetOS)
# ==============================================================================


import os
import threading
import telebot
import config

from dotenv import load_dotenv
from config import (
    GREEN,
    YELLOW,
    RED,
    CYAN,
    RESET,
    VERSION,
    ENV_PATH
    )


# Иницилизируем бота
def init_bot():
    load_dotenv(ENV_PATH)
    config.TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    notifications_str = os.getenv("TELEGRAM_BOT_NOTIFICATION", "false").lower().strip()
    config.TELEGRAM_BOT_NOTIFICATION = notifications_str in ("true", "1", "on", "yes") 

    if not config.TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN not found in .env")
        return False

    try:
        config.TELEGRAM_BOT = telebot.TeleBot(config.TELEGRAM_TOKEN)
        config.TELEGRAM_BOT_RUNNING = True
        #bot_info = config.TELEGRAM_BOT.get_me()
        #print(f"{GREEN}✅ Telegram bot connected: @{bot_info.username}{RESET}")

    except Exception as e:
        print(f"{RED}❌ Telegram bot auth failed: {e}{RESET}")
        config.TELEGRAM_BOT_RUNNING = False
        return False

    # Обработка команд в Telegram боте
    # Обработка /start
    @config.TELEGRAM_BOT.message_handler(commands=["start"])
    def tg_start(message):
        save_user(message.chat.id)
        config.TELEGRAM_BOT.send_message(
            message.chat.id,
            (
            "🤖 *TetOS connected*\n"
            "You are registered in the system.\n"
            "You will receive server notifications.\n"
            "Type /help to see available commands.\n"
            ),
            parse_mode="Markdown"
        )

    # Обработка /help
    @config.TELEGRAM_BOT.message_handler(commands=["help"])
    def tg_help(message):
        config.TELEGRAM_BOT.send_message(
            message.chat.id,
            (
                "📖 *TetOS commands*\n\n"
                "/start — start bot\n"
                "/info — server info\n"
                "/status - status server (on/off)\n"
                "/help — show this message"
            ),
            parse_mode="Markdown"
        )


    # Обработка /info
    @config.TELEGRAM_BOT.message_handler(commands=["info"])
    def tg_info(message):
        status_text = "🟢 Server is ON" if config.SERVER_IS_READY else "🔴 Server is OFF"

        text = (
            "ℹ️ *Server info*\n\n"
            f"{status_text}\n"
        )

        if config.SERVER_IS_READY:
            text += (
                f"📦 Version Minecraft: {config.SERVER_MC_VERSION}\n"
                f"🎮 Online players: {config.SERVER_ONLINE_PLAYERS} / {config.SERVER_MAX_PLAYERS}\n"
                f"🌐 IP (Hamachi): `{config.SERVER_IP}:{config.SERVER_PORT}`\n"
                f"📡 IP (Local): `{config.SERVER_LOCAL_IP}:{config.SERVER_PORT}`\n"
            )

        config.TELEGRAM_BOT.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown"
        )


    # Обработка /status
    @config.TELEGRAM_BOT.message_handler(commands=["status"])
    def tg_info(message):
        status_text = "🟢 Server is ON" if config.SERVER_IS_READY else "🔴 Server is OFF"

        text = (
            "ℹ️ *Server status*\n\n"
            f"{status_text}\n"
        )

        config.TELEGRAM_BOT.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown"
        )


    # Обработка ВСЕГО.
    @config.TELEGRAM_BOT.message_handler(func=lambda message: True)
    def echo_all(message):
        config.TELEGRAM_BOT.send_message(
            message.chat.id,
            "❓ Unknown command.\nType /help to see available commands."
        )


    # Функция для запуска Telegram бота, бесконечная робота пока утилита живёт
    def run_bot():
        try:
            config.TELEGRAM_BOT.infinity_polling(skip_pending=True)#timeout=15, long_polling_timeout=30)
            TELEGRAM_BOT_RUNNING = True
        except Exception as e:
            print(f"{RED}❌ Telegram bot crashed: {e}{RESET}")

    # Переводим Telegram бота в отдельный поток
    TELEGRAM_BOT_THREAD = threading.Thread(target=run_bot, daemon=True)
    TELEGRAM_BOT_THREAD.start()
    return True


# ===== Загружаем Telegram юзеров =====
def load_users():
    if not config.TELEGRAM_USERS_FILE.exists():
        return set()
    return set(config.TELEGRAM_USERS_FILE.read_text().splitlines())


# ===== Сохраняем Telegram юзеров =====
def save_user(user_id):
    users = load_users()
    users.add(str(user_id))
    config.TELEGRAM_USERS_FILE.write_text("\n".join(users))


# ===== Уведомляем всех Telegram юзеров =====
def broadcast(message, parse_mode="Markdown"):
    if config.TELEGRAM_BOT is None or config.TELEGRAM_BOT_NOTIFICATION is False:
        return
    for user_id in load_users():
        try:
            config.TELEGRAM_BOT.send_message(user_id, message, parse_mode=parse_mode if parse_mode else None)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")


# ===== Уведомляем про запуск сервера =====
def notify_server_ready():
    if not config.TELEGRAM_BOT_NOTIFICATION:
        return

    broadcast(
        f"🟢 *Minecraft server started*\n\n"
        f"📦 Verison Minecraft: {config.SERVER_MC_VERSION}\n"
        f"🌐 IP (Hamachi): `{config.SERVER_IP}:{config.SERVER_PORT}`\n"
        f"📡 IP (Local): `{config.SERVER_LOCAL_IP}:{config.SERVER_PORT}`\n"
        )

# ===== Уведомляем про остановку сервера =====
def notify_server_stopped():
    if not config.TELEGRAM_BOT_NOTIFICATION:
        return

    broadcast("🔴 *Minecraft server stopped*")


# ===== Уведомляем про рестарт сервера =====
def notify_server_restarted():
    if not config.TELEGRAM_BOT_NOTIFICATION:
        return

    broadcast("🔄 *Minecraft server restarting*")


# ===== Функция для остановки бота =====
def stop_bot():
    print("W.I.P")


# ===== Функция для перезапуска бота =====
def reload_bot():
    print("W.I.P")
