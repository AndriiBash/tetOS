import os
import threading
import telebot

from dotenv import load_dotenv
from config import *

def init_bot():
    global TELEGRAM_BOT, TELEGRAM_BOT_THREAD

    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN not found in .env")
        return False

    TELEGRAM_BOT = telebot.TeleBot(TELEGRAM_TOKEN)


    # Обработка команд в Telegram боте
    @TELEGRAM_BOT.message_handler(commands=["start"])
    def tg_start(message):
        save_user(message.chat.id)
        TELEGRAM_BOT.send_message(
            message.chat.id,
            "🤖 TetOS connected.\nYou will receive server notifications."
        )

    def run_bot():
        try:
            TELEGRAM_BOT.infinity_polling(skip_pending=True)
        except Exception as e:
            print(f"{RED}❌ Telegram bot crashed: {e}{RESET}")

    TELEGRAM_BOT_THREAD = threading.Thread(target=run_bot, daemon=True)
    TELEGRAM_BOT_THREAD.start()
    return True


# ===== Загружаем Telegram юзеров =====
def load_users():
    if not TELEGRAM_USERS_FILE.exists():
        return set()
    return set(TELEGRAM_USERS_FILE.read_text().splitlines())


# ===== Сохраняем Telegram юзеров =====
def save_user(user_id):
    users = load_users()
    users.add(str(user_id))
    TELEGRAM_USERS_FILE.write_text("\n".join(users))


# ===== Уведомляем всех Telegram юзеров =====
def broadcast(message):
    if TELEGRAM_BOT is None:
        return
    for user_id in load_users():
        try:
            TELEGRAM_BOT.send_message(user_id, message)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")