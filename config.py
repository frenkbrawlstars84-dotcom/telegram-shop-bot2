"""Загрузка конфигурации из .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "Не задан BOT_TOKEN. Скопируйте .env.example в .env и заполните значения."
    )

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except ValueError:
    raise RuntimeError("ADMIN_ID должен быть числом (Telegram ID администратора).")

if not ADMIN_ID:
    raise RuntimeError("Не задан ADMIN_ID в .env.")

# Реквизиты LiqPay (используются в заглушке оплаты)
LIQPAY_PUBLIC_KEY = os.getenv("LIQPAY_PUBLIC_KEY", "")
LIQPAY_PRIVATE_KEY = os.getenv("LIQPAY_PRIVATE_KEY", "")

# Путь к файлу базы данных SQLite
DB_PATH = str(BASE_DIR / "shop.db")

# Валюта магазина
CURRENCY = "₴"
