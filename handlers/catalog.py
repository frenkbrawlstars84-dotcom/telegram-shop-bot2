"""Каталог: категории, список товаров, добавление в корзину."""
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from config import CURRENCY
from database import db
from keyboards import categories_kb, products_kb

router = Router()


async def _show_categories(target: Message | CallbackQuery) -> None:
    categories = await db.get_categories()
    if not categories:
        text = "😔 Каталог пока пуст. Загляните позже!"
        if isinstance(target, CallbackQuery):
            await target.message.answer(text)
        else:
            await target.answer(text)
        return

    text = "🛍 <b>Категории товаров</b>\nВыберите категорию:"
    kb = categories_kb(categories)
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.message(F.text == "🛍 Каталог")
async def catalog_button(message: Message) -> None:
    await _show_categories(message)


@router.callback_query(F.data == "catalog")
async def catalog_back(callback: CallbackQuery) -> None:
    await _show_categories(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_products(callback: CallbackQuery) -> None:
    category_id = int(callback.data.split(":", 1)[1])
    products = await db.get_products(category_id)

    if not products:
        await callback.answer("В этой категории пока нет товаров.", show_alert=True)
        return

    # Карточка каждого товара: фото + описание отдельным сообщением.
    for p in products:
        caption = (
            f"<b>{p['name']}</b>\n"
            f"{p['description']}\n\n"
            f"Цена: <b>{p['price']:.0f} {CURRENCY}</b>"
        )
        if p["photo"]:
            try:
                await callback.message.answer_photo(p["photo"], caption=caption)
                continue
            except Exception:
                # Если фото недоступно (битый URL/file_id) — шлём текстом.
                pass
        await callback.message.answer(caption)

    await callback.message.answer(
        "Добавьте товары в корзину 👇",
        reply_markup=products_kb(products, category_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add:"))
async def add_product(callback: CallbackQuery) -> None:
    product_id = int(callback.data.split(":", 1)[1])
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("Товар не найден 😔", show_alert=True)
        return

    await db.add_to_cart(callback.from_user.id, product_id)
    await callback.answer(f"«{product['name']}» добавлен в корзину ✅")
