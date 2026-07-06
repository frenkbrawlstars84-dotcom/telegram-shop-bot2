"""Корзина: просмотр, удаление позиции, очистка."""
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from config import CURRENCY
from database import db
from keyboards import cart_kb

router = Router()


def render_cart(items) -> str:
    """Формирует текст корзины с итоговой суммой."""
    lines = ["🛒 <b>Ваша корзина</b>\n"]
    total = 0.0
    for it in items:
        subtotal = it["quantity"] * it["price"]
        total += subtotal
        lines.append(
            f"• {it['name']} — {it['quantity']} × {it['price']:.0f} "
            f"= <b>{subtotal:.0f} {CURRENCY}</b>"
        )
    lines.append(f"\nИтого: <b>{total:.0f} {CURRENCY}</b>")
    return "\n".join(lines)


async def _show_cart(target: Message | CallbackQuery) -> None:
    user_id = target.from_user.id
    items = await db.get_cart(user_id)

    if not items:
        text = "🛒 Ваша корзина пуста.\nЗагляните в «🛍 Каталог»!"
        if isinstance(target, CallbackQuery):
            await target.message.answer(text)
        else:
            await target.answer(text)
        return

    text = render_cart(items)
    kb = cart_kb(items)
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.message(F.text == "🛒 Корзина")
async def cart_button(message: Message) -> None:
    await _show_cart(message)


@router.callback_query(F.data == "cart")
async def cart_back(callback: CallbackQuery) -> None:
    await _show_cart(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("del:"))
async def delete_item(callback: CallbackQuery) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    await db.remove_from_cart(callback.from_user.id, product_id)
    await callback.answer("Товар удалён 🗑")

    # Обновляем сообщение с корзиной.
    items = await db.get_cart(callback.from_user.id)
    if items:
        await callback.message.edit_text(render_cart(items), reply_markup=cart_kb(items))
    else:
        await callback.message.edit_text("🛒 Корзина пуста.")


@router.callback_query(F.data == "cart_clear")
async def clear(callback: CallbackQuery) -> None:
    await db.clear_cart(callback.from_user.id)
    await callback.answer("Корзина очищена 🧹")
    await callback.message.edit_text("🛒 Корзина пуста.")
