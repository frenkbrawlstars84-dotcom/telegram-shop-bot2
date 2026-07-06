"""Работа с базой данных SQLite (через aiosqlite)."""
import aiosqlite

from config import DB_PATH

# --- SQL для создания схемы ---
SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    description TEXT    DEFAULT '',
    price       REAL    NOT NULL,
    photo       TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS cart_items (
    user_id    INTEGER NOT NULL,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity   INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    phone      TEXT    NOT NULL,
    address    TEXT    NOT NULL,
    items      TEXT    NOT NULL,   -- текстовое описание позиций
    total      REAL    NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'new',
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


async def init_db() -> None:
    """Создаёт таблицы и наполняет магазин демо-данными при первом запуске."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.executescript(SCHEMA)
        await db.commit()
        await _seed_if_empty(db)


async def _seed_if_empty(db: aiosqlite.Connection) -> None:
    """Наполняет каталог демо-товарами, если он пуст."""
    async with db.execute("SELECT COUNT(*) FROM categories") as cur:
        (count,) = await cur.fetchone()
    if count:
        return

    from database.seed import DEMO_CATEGORIES

    for cat_name, products in DEMO_CATEGORIES:
        cursor = await db.execute(
            "INSERT INTO categories (name) VALUES (?)", (cat_name,)
        )
        category_id = cursor.lastrowid
        for p in products:
            await db.execute(
                "INSERT INTO products (category_id, name, description, price, photo) "
                "VALUES (?, ?, ?, ?, ?)",
                (category_id, p["name"], p["description"], p["price"], p["photo"]),
            )
    await db.commit()


# --- Категории и товары ---
async def get_categories() -> list[aiosqlite.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, name FROM categories ORDER BY name") as cur:
            return await cur.fetchall()


async def get_products(category_id: int) -> list[aiosqlite.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, name, description, price, photo FROM products "
            "WHERE category_id = ? ORDER BY name",
            (category_id,),
        ) as cur:
            return await cur.fetchall()


async def get_product(product_id: int) -> aiosqlite.Row | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, name, description, price, photo FROM products WHERE id = ?",
            (product_id,),
        ) as cur:
            return await cur.fetchone()


# --- Корзина ---
async def add_to_cart(user_id: int, product_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, 1) "
            "ON CONFLICT(user_id, product_id) "
            "DO UPDATE SET quantity = quantity + 1",
            (user_id, product_id),
        )
        await db.commit()


async def get_cart(user_id: int) -> list[aiosqlite.Row]:
    """Возвращает позиции корзины с данными товара."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT c.product_id, c.quantity, p.name, p.price "
            "FROM cart_items c JOIN products p ON p.id = c.product_id "
            "WHERE c.user_id = ? ORDER BY p.name",
            (user_id,),
        ) as cur:
            return await cur.fetchall()


async def remove_from_cart(user_id: int, product_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        )
        await db.commit()


async def clear_cart(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
        await db.commit()


async def cart_total(user_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COALESCE(SUM(c.quantity * p.price), 0) "
            "FROM cart_items c JOIN products p ON p.id = c.product_id "
            "WHERE c.user_id = ?",
            (user_id,),
        ) as cur:
            (total,) = await cur.fetchone()
    return float(total)


# --- Заказы ---
async def create_order(
    user_id: int,
    name: str,
    phone: str,
    address: str,
    items: str,
    total: float,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, name, phone, address, items, total) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, name, phone, address, items, total),
        )
        await db.commit()
        return cursor.lastrowid


async def set_order_status(order_id: int, status: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE orders SET status = ? WHERE id = ?", (status, order_id)
        )
        await db.commit()
