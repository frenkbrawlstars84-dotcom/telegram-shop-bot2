"""Оформление заказа (FSM), уведомление админу и оплата LiqPay (заглушка)."""
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Contact, Message, ReplyKeyboardRemove

from config import ADMIN_ID, CURRENCY
from database import db
from keyboards import admin_order_kb, main_menu, pay_kb, phone_request_kb
from services.liqpay import payment_instructions

router = Router()

PHONE_RE = re.compile(r"^[\d\s\-\+\(\)]{7,20}$")


class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext) -> None:
    items = await db.get_cart(callback.from_user.id)
    if not items:
        await callback.answer("Корзина пуста — нечего оформлять.", show_alert=True)
        return

    await state.set_state(OrderForm.name)
    await callback.message.answer(
        "📝 Оформление заказа.\n\nКак вас зовут? (ФИО получателя)",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer()


@router.message(OrderForm.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введите корректное имя.")
        return
    await state.update_data(name=name)
    await state.set_state(OrderForm.phone)
    await message.answer(
        "📱 Укажите номер телефона для связи.\n"
        "Можно нажать кнопку ниже или ввести вручную.",
        reply_markup=phone_request_kb(),
    )


@router.message(OrderForm.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext) -> None:
    await _save_phone(message, state, message.contact.phone_number)


@router.message(OrderForm.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    if not PHONE_RE.match(phone):
        await message.answer("Похоже, номер некорректный. Попробуйте ещё раз.")
        return
    await _save_phone(message, state, phone)


async def _save_phone(message: Message, state: FSMContext, phone: str) -> None:
    await state.update_data(phone=phone)
    await state.set_state(OrderForm.address)
    await message.answer(
        "🏠 Укажите адрес доставки (город, отделение / улица, дом, квартира).",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(OrderForm.address, F.text)
async def process_address(message: Message, state: FSMContext) -> None:
    address = message.text.strip()
    if len(address) < 5:
        await message.answer("Пожалуйста, укажите более подробный адрес.")
        return

    data = await state.get_data()
    user_id = message.from_user.id

    items = await db.get_cart(user_id)
    if not items:
        await state.clear()
        await message.answer("Корзина опустела. Начните заказ заново.", reply_markup=main_menu())
        return

    total = await db.cart_total(user_id)
    items_text = "\n".join(
        f"• {it['name']} — {it['quantity']} × {it['price']:.0f} {CURRENCY}"
        for it in items
    )

    order_id = await db.create_order(
        user_id=user_id,
        name=data["name"],
        phone=data["phone"],
        address=address,
        items=items_text,
        total=total,
    )

    await db.clear_cart(user_id)
    await state.clear()

    # Подтверждение пользователю
    await message.answer(
        f"✅ Заказ №{order_id} оформлен!\n\n"
        f"👤 {data['name']}\n"
        f"📱 {data['phone']}\n"
        f"🏠 {address}\n\n"
        f"{items_text}\n\n"
        f"Итого: <b>{total:.0f} {CURRENCY}</b>\n\n"
        "Осталось оплатить заказ 👇",
        reply_markup=main_menu(),
    )
    await message.answer(
        "Нажмите кнопку для перехода к оплате:",
        reply_markup=pay_kb(order_id),
    )

    # Уведомление админу
    await _notify_admin(
        message,
        order_id=order_id,
        name=data["name"],
        phone=data["phone"],
        address=address,
        items_text=items_text,
        total=total,
    )


async def _notify_admin(
    message: Message,
    order_id: int,
    name: str,
    phone: str,
    address: str,
    items_text: str,
    total: float,
) -> None:
    user = message.from_user
    username = f"@{user.username}" if user.username else f"id{user.id}"
    admin_text = (
        f"🔔 <b>Новый заказ №{order_id}</b>\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n"
        f"🏠 Адрес: {address}\n"
        f"🆔 Клиент: {username} (id {user.id})\n\n"
        f"<b>Состав:</b>\n{items_text}\n\n"
        f"💰 Сумма: <b>{total:.0f} {CURRENCY}</b>"
    )
    try:
        await message.bot.send_message(
            ADMIN_ID, admin_text, reply_markup=admin_order_kb(order_id)
        )
    except Exception:
        # Админ не начал диалог с ботом или неверный ADMIN_ID — не роняем заказ.
        pass


# --- Оплата (заглушка LiqPay) ---
@router.callback_query(F.data.startswith("pay:"))
async def pay_order(callback: CallbackQuery) -> None:
    order_id = int(callback.data.split(":", 1)[1])
    # Сумму берём из заказа
    from config import DB_PATH
    import aiosqlite

    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute(
            "SELECT total FROM orders WHERE id = ?", (order_id,)
        ) as cur:
            row = await cur.fetchone()

    if not row:
        await callback.answer("Заказ не найден.", show_alert=True)
        return

    amount = float(row[0])
    await callback.message.answer(payment_instructions(order_id, amount))
    await callback.answer()


# --- Действия админа над заказом ---
@router.callback_query(F.data.startswith("adm_ok:"))
async def admin_accept(callback: CallbackQuery) -> None:
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = int(callback.data.split(":", 1)[1])
    await db.set_order_status(order_id, "accepted")
    await callback.answer("Заказ принят ✅")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Заказ №{order_id}: статус «принят».")


@router.callback_query(F.data.startswith("adm_no:"))
async def admin_reject(callback: CallbackQuery) -> None:
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    order_id = int(callback.data.split(":", 1)[1])
    await db.set_order_status(order_id, "rejected")
    await callback.answer("Заказ отклонён ❌")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Заказ №{order_id}: статус «отклонён».")
