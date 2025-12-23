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
from telebot.formatting import mcode
from config import (
    GREEN,
    YELLOW,
    RED,
    CYAN,
    RESET,
    VERSION
    )



# Иницилизируем бота
def init_bot():
    load_dotenv()
    config.TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not config.TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN not found in .env")
        return False

    config.TELEGRAM_BOT = telebot.TeleBot(config.TELEGRAM_TOKEN)


    # Обработка команд в Telegram боте
    @config.TELEGRAM_BOT.message_handler(commands=["start"])
    def tg_start(message):
        save_user(message.chat.id)
        config.TELEGRAM_BOT.send_message(
            message.chat.id,
            "🤖 TetOS connected.\nYou will receive server notifications."
        )

    def run_bot():
        try:
            config.TELEGRAM_BOT.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"{RED}❌ Telegram bot crashed: {e}{RESET}")

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
def broadcast(message):
    if config.TELEGRAM_BOT is None:
        return
    for user_id in load_users():
        try:
            config.TELEGRAM_BOT.send_message(user_id, message)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")


# ===== Уведомляем про запуск сервера =====
def notify_server_ready():
    broadcast(f"""
        🟢 Minecraft server started
        Verison: {config.SERVER_MC_VERSION}
        IP (Hamachi): {config.SERVER_IP}:{config.SERVER_PORT}
        Another info...
        """)

# ===== Уведомляем про остановку сервера =====
def notify_server_stopped():
    broadcast("🔴 Minecraft server stopped")


# ===== Уведомляем про рестарт сервера =====
def notify_server_restarted():
    broadcast("🔄 Minecraft server restarting")
