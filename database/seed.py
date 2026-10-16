"""Демо-данные каталога, которыми наполняется пустая база при первом запуске.

Поле "photo" — это либо URL картинки, либо file_id из Telegram.
Оставьте пустым (""), если фото не нужно.
"""

DEMO_CATEGORIES = [
    (
        "Электроника",
        [
            {
                "name": "Наушники TWS Pro",
                "description": "Беспроводные наушники с шумоподавлением, 24 ч работы.",
                "price": 50.99,
                "photo": "https://picsum.photos/seed/headphones/600/400",
            },
            {
                "name": "Умные часы Watch S",
                "description": "AMOLED-экран, пульсометр, GPS, защита IP68.",
                "price": 100,
                "photo": "https://picsum.photos/seed/watch/600/400",
            },
            {
                "name": "Портативная колонка Boom",
                "description": "Bluetooth 5.3, 20 Вт, влагозащита.",
                "price": 60,
                "photo": "https://picsum.photos/seed/speaker/600/400",
            },
        ],
    ),
    (
        "Одежда",
        [
            {
                "name": "Футболка Basic",
                "description": "100% хлопок, унисекс, размеры S–XXL.",
                "price": 40,
                "photo": "https://picsum.photos/seed/tshirt/600/400",
            },
            {
                "name": "Худи Oversize",
                "description": "Тёплое худи с начёсом, свободный крой.",
                "price": 30,
                "photo": "https://picsum.photos/seed/hoodie/600/400",
            },
        ],
    ),
    (
        "Аксессуары",
        [
            {
                "name": "Рюкзак City",
                "description": "Отделение для ноутбука 15\", водоотталкивающая ткань.",
                "price": 50,
                "photo": "https://picsum.photos/seed/backpack/600/400",
            },
            {
                "name": "Термокружка 500 мл",
                "description": "Сталь, держит тепло до 12 часов.",
                "price": 39,
                "photo": "https://picsum.photos/seed/mug/600/400",
            },
        ],
    ),
]
