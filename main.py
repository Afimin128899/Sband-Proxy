import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command

from flyerapi import Flyer
from db import init_db, add_user, get_users

logging.basicConfig(level=logging.INFO)

# ================= ENV =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FLYER_API_KEY = os.environ.get("FLYER_API_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

# ================= PROXY =================
SOCKS_SERVER = "193.124.133.42"
SOCKS_PORT = "58976"
SOCKS_USER = "VxWwEWV95B"
SOCKS_PASS = "ea2pSdiR8Y"

# ================= INIT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
flyer = Flyer(FLYER_API_KEY)

broadcast_mode = False


@dp.message(CommandStart())
async def start(message: types.Message):
    await add_user(message.from_user.id)

    await message.answer(
        "👋 Привет!\n\n"
        "Для доступа нужно выполнить задания / подписаться."
    )


@dp.message(Command("broadcast"))
async def broadcast_start(message: types.Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = True
    await message.answer(
        "✉️ Отправь сообщение для рассылки всем пользователям\n"
        "❌ /cancel — отмена"
    )


@dp.message(Command("cancel"))
async def broadcast_cancel(message: types.Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = False
    await message.answer("❌ Рассылка отменена")


@dp.message()
async def check(message: types.Message):
    global broadcast_mode

    # ===== РАССЫЛКА =====
    if broadcast_mode and message.from_user.id == ADMIN_ID:
        users = await get_users()
        sent, failed = 0, 0

        for uid in users:
            try:
                await message.copy_to(uid)
                sent += 1
            except:
                failed += 1

        broadcast_mode = False
        await message.answer(
            f"✅ Рассылка завершена\n"
            f"📤 Отправлено: {sent}\n"
            f"❌ Ошибок: {failed}"
        )
        return

    # ===== ПРОВЕРКА FLYER =====
    ok = await flyer.check(
        user_id=message.from_user.id,
        language_code=message.from_user.language_code,
    )

    if not ok:
        return

    socks_link = (
        f"https://t.me/socks?"
        f"server={SOCKS_SERVER}"
        f"&port={SOCKS_PORT}"
        f"&user={SOCKS_USER}"
        f"&pass={SOCKS_PASS}"
    )

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔗 Подключить прокси",
                    url=socks_link
                )
            ]
        ]
    )

    await message.answer(
        "✅ Доступ разрешён!\n\n"
        "Нажми кнопку ниже, чтобы подключить прокси.",
        reply_markup=keyboard
    )


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
