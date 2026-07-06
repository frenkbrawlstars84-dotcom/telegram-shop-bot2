"""Команды /start, /help и главное меню."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards import main_menu

router = Router()

WELCOME = (
    "👋 Добро пожаловать в наш магазин!\n\n"
    "Здесь вы можете:\n"
    "• 🛍 посмотреть <b>каталог</b> товаров по категориям\n"
    "• 🛒 собрать <b>корзину</b>\n"
    "• ✅ оформить <b>заказ</b> с доставкой\n\n"
    "Выберите действие в меню ниже 👇"
)

HELP = (
    "ℹ️ <b>Как пользоваться ботом</b>\n\n"
    "1. Нажмите «🛍 Каталог» и выберите категорию.\n"
    "2. Добавляйте товары кнопкой «➕».\n"
    "3. Откройте «🛒 Корзина», проверьте состав.\n"
    "4. Нажмите «✅ Оформить» и укажите имя, телефон и адрес.\n"
    "5. После оформления придёт ссылка на оплату.\n\n"
    "Команды: /start — меню, /help — эта справка."
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=main_menu())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP, reply_markup=main_menu())
