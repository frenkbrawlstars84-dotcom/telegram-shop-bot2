"""Клавиатуры (inline и reply) для бота."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CURRENCY


def main_menu() -> ReplyKeyboardMarkup:
    """Нижнее меню, всегда под рукой."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )


def categories_kb(categories) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat in categories:
        kb.button(text=cat["name"], callback_data=f"cat:{cat['id']}")
    kb.adjust(2)
    return kb.as_markup()


def products_kb(products, category_id: int) -> InlineKeyboardMarkup:
    """Для каждого товара — кнопка "в корзину"; снизу возврат к категориям."""
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(
            text=f"➕ {p['name']} — {p['price']:.0f} {CURRENCY}",
            callback_data=f"add:{p['id']}",
        )
    kb.button(text="⬅️ К категориям", callback_data="catalog")
    kb.adjust(1)
    return kb.as_markup()


def cart_kb(items) -> InlineKeyboardMarkup:
    """Кнопки удаления для каждой позиции + очистка и оформление."""
    kb = InlineKeyboardBuilder()
    for it in items:
        kb.button(
            text=f"🗑 {it['name']}",
            callback_data=f"del:{it['product_id']}",
        )
    kb.adjust(1)
    kb.row(
        InlineKeyboardButton(text="🧹 Очистить", callback_data="cart_clear"),
        InlineKeyboardButton(text="✅ Оформить", callback_data="checkout"),
    )
    return kb.as_markup()


def phone_request_kb() -> ReplyKeyboardMarkup:
    """Reply-клавиатура с кнопкой отправки контакта."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить мой номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def pay_kb(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Оплатить через LiqPay", callback_data=f"pay:{order_id}")
    kb.adjust(1)
    return kb.as_markup()


def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    """Кнопки для админа под уведомлением о заказе."""
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Принять", callback_data=f"adm_ok:{order_id}")
    kb.button(text="❌ Отклонить", callback_data=f"adm_no:{order_id}")
    kb.adjust(2)
    return kb.as_markup()
