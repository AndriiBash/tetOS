# ==============================================================================
# test.py
# ==============================================================================
# Author:      AndriiBash
# Created:     2026-05-17
# Project:     TetOS (github.com/AndriiBash/tetOS)
# ==============================================================================

import time

import config
import server_commands

from telegram_bot import (
    init_bot,
    broadcast,
    notify_server_ready,
    notify_server_stopped,
    notify_server_restarted
)


# ==============================================================================
# SERVER TESTS
# ==============================================================================

def test_start_server():
    print("\n=== TEST: start server ===")

    server_commands.start_server()

    time.sleep(5)

    if config.SERVER_PROCESS is not None:
        print("[PASS] Сервер успішно запущений")
        return True

    print("[FAIL] Помилка запуску серверу")
    return False


def test_stop_server():
    print("\n=== TEST: stop server ===")

    server_commands.stop_server()

    time.sleep(3)

    if config.SERVER_PROCESS is None:
        print("[PASS] Сервер успішно зупинений")
        return True

    print("[FAIL] Сервер не був зупинений")
    return False


def test_fetch_tps():
    print("\n=== TEST: fetch TPS ===")

    try:
        tps = server_commands.fetch_tps()

        if tps is not None:
            print(f"[PASS] TPS отримано: {tps}")
            return True

    except Exception as e:
        print("[FAIL] Помилка отримання TPS:", e)

    return False


def test_ram_monitoring():
    print("\n=== TEST: RAM monitoring ===")

    try:
        ram = server_commands.get_used_ram()

        if ram >= 0:
            print(f"[PASS] Використання RAM: {ram} MB")
            return True

    except Exception as e:
        print("[FAIL] Помилка моніторингу RAM:", e)

    return False


# ==============================================================================
# CONFIG TESTS
# ==============================================================================

def test_update_server_property():
    print("\n=== TEST: update server.properties ===")

    try:
        result = server_commands.update_server_property(
            "max-players",
            "20"
        )

        if result:
            print("[PASS] Конфігурацію оновлено")
            return True

    except Exception as e:
        print("[FAIL] Помилка оновлення конфігурації:", e)

    return False


# ==============================================================================
# TELEGRAM TESTS
# ==============================================================================

def test_telegram_init():
    print("\n=== TEST: telegram bot init ===")

    try:
        init_bot()

        if config.TELEGRAM_BOT is not None:
            print("[PASS] Telegram-бот успішно ініціалізований")
            return True

    except Exception as e:
        print("[FAIL] Помилка ініціалізації Telegram-бота:", e)

    return False


def test_telegram_notification():
    print("\n=== TEST: telegram notification ===")

    try:
        broadcast("✅ TetOS test notification")
        print("[PASS] Telegram повідомлення надіслано")
        return True

    except Exception as e:
        print("[FAIL] Помилка Telegram:", e)

    return False


def test_telegram_events():
    print("\n=== TEST: telegram event notifications ===")

    try:
        notify_server_ready()
        notify_server_restarted()
        notify_server_stopped()

        print("[PASS] Telegram event notifications успішні")
        return True

    except Exception as e:
        print("[FAIL] Помилка Telegram event notifications:", e)

    return False


# ==============================================================================
# RUN ALL TESTS
# ==============================================================================

def test_system():
    print("\n")
    print("========================================")
    print("         TetOS SYSTEM TESTS")
    print("========================================")

    passed = 0
    failed = 0

    tests = [
        test_telegram_init,
        test_start_server,
        test_fetch_tps,
        test_ram_monitoring,
        test_update_server_property,
        test_telegram_notification,
        test_telegram_events,
        test_stop_server,
    ]

    for test in tests:
        try:
            result = test()

            if result:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            failed += 1
            print(f"[ERROR] {test.__name__}: {e}")

    print("\n========================================")
    print("             TEST RESULTS")
    print("========================================")
    print(f"[PASS] Успішно: {passed}")
    print(f"[FAIL] Помилки: {failed}")
    print("========================================")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    test_system()