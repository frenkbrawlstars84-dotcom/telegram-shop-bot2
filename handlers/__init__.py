"""Регистрация всех роутеров бота."""
from aiogram import Router

from handlers import cart, catalog, order, start


def get_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(catalog.router)
    router.include_router(cart.router)
    router.include_router(order.router)
    return router
