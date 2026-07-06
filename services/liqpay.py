"""Интеграция с LiqPay — ЗАГЛУШКА.

Здесь реализована генерация подписи по официальному алгоритму LiqPay
(base64(data) + подпись), но фактический запрос к платёжному шлюзу НЕ
выполняется. Функция payment_stub() возвращает готовые данные, которые
достаточно вставить в HTML-форму / ссылку, когда вы включите боевой режим.

------------------------------------------------------------------------
КАК ПОДКЛЮЧИТЬ РЕАЛЬНУЮ ОПЛАТУ
------------------------------------------------------------------------
1. Зарегистрируйтесь на https://www.liqpay.ua и создайте компанию/магазин.
2. В личном кабинете получите public_key и private_key.
   Пропишите их в .env:
       LIQPAY_PUBLIC_KEY=...
       LIQPAY_PRIVATE_KEY=...
3. Оплата в LiqPay работает через веб-форму: пользователю нужно открыть
   URL https://www.liqpay.ua/api/3/checkout с параметрами data и signature.
   В Telegram это делается через кнопку-ссылку (WebApp или обычный URL).
4. Чтобы узнать результат оплаты, настройте server_url (callback):
   LiqPay шлёт POST на ваш публичный HTTPS-эндпоинт. Нужен веб-сервер
   (например, aiohttp/FastAPI) с публичным доменом. В callback проверьте
   подпись и обновите статус заказа (database.set_order_status).
5. Подпись считается так (уже реализовано ниже):
       signature = base64( sha1( private_key + data + private_key ) )
   где data = base64( json_с_параметрами_платежа ).

Полезные ссылки:
   • Документация: https://www.liqpay.ua/documentation/api/aquiring/checkout
   • Проверка оплаты: https://www.liqpay.ua/documentation/api/callback
------------------------------------------------------------------------
"""
import base64
import hashlib
import json

from config import CURRENCY, LIQPAY_PRIVATE_KEY, LIQPAY_PUBLIC_KEY

CHECKOUT_URL = "https://www.liqpay.ua/api/3/checkout"


def _make_data(order_id: int, amount: float, description: str) -> str:
    """Формирует base64-строку data для LiqPay."""
    payload = {
        "public_key": LIQPAY_PUBLIC_KEY,
        "version": "3",
        "action": "pay",
        "amount": round(amount, 2),
        "currency": "UAH",
        "description": description,
        "order_id": str(order_id),
        # В боевом режиме укажите публичный HTTPS-адрес callback-обработчика:
        # "server_url": "https://ваш-домен/liqpay/callback",
    }
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")


def _make_signature(data: str) -> str:
    """Подпись: base64( sha1( private + data + private ) )."""
    to_sign = (LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY).encode("utf-8")
    return base64.b64encode(hashlib.sha1(to_sign).digest()).decode("utf-8")


def payment_stub(order_id: int, amount: float) -> dict:
    """Возвращает данные для оплаты (без реального обращения к шлюзу).

    В боевом режиме этими data/signature наполняется checkout-форма LiqPay
    или формируется ссылка на оплату.
    """
    description = f"Оплата заказа №{order_id}"
    data = _make_data(order_id, amount, description)
    signature = _make_signature(data)
    return {
        "checkout_url": CHECKOUT_URL,
        "data": data,
        "signature": signature,
        "amount": amount,
    }


def payment_instructions(order_id: int, amount: float) -> str:
    """Текст-заглушка, который показывается пользователю вместо реальной оплаты."""
    info = payment_stub(order_id, amount)
    return (
        f"💳 <b>Оплата заказа №{order_id}</b>\n\n"
        f"Сумма к оплате: <b>{amount:.2f} {CURRENCY}</b>\n\n"
        "⚠️ <i>Это демонстрационная заглушка LiqPay.</i>\n"
        "Реальное списание средств не производится.\n\n"
        "Чтобы включить боевую оплату:\n"
        "1. Укажите ключи LIQPAY_PUBLIC_KEY / LIQPAY_PRIVATE_KEY в .env\n"
        "2. Поднимите HTTPS-эндпоинт для callback\n"
        "3. Отдавайте пользователю checkout-форму LiqPay\n\n"
        "Технические данные платежа уже сгенерированы:\n"
        f"<code>data={info['data'][:40]}...</code>\n\n"
        "Подробности — в <code>services/liqpay.py</code>."
    )
