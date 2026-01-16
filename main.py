import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from flyerapi import Flyer
from db import (
    init_db,
    add_user,
    has_access,
    set_access_granted,
    get_users,
)

logging.basicConfig(level=logging.INFO)

# ================= ENV =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FLYER_API_KEY = os.environ.get("FLYER_API_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# ================= PROXY =================
SOCKS_SERVER = "193.124.133.42"
SOCKS_PORT = "58976"
SOCKS_USER = "VxWwEWV95B"
SOCKS_PASS = "ea2pSdiR8Y"

BOT_USERNAME = "IMYA_TVOEGO_BOTA"

# ================= INIT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
flyer = Flyer(FLYER_API_KEY)

broadcast_mode = False


# ================= KEYBOARDS =================
def menu_keyboard():
    socks_link = (
        f"https://t.me/socks?"
        f"server={SOCKS_SERVER}"
        f"&port={SOCKS_PORT}"
        f"&user={SOCKS_USER}"
        f"&pass={SOCKS_PASS}"
    )

    share_text = (
        "🚀 Telegram стал работать медленно?\n\n"
        "Подключи прокси за 1 клик 👌\n\n"
        f"👉 https://t.me/{BOT_USERNAME}"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Подключить прокси",
                    url=socks_link
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Поделиться с другом",
                    switch_inline_query=share_text
                )
            ],
        ]
    )


def check_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Проверить задания",
                    callback_data="check_tasks"
                )
            ]
        ]
    )


# ================= START =================
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    await add_user(user_id)

    if await has_access(user_id):
        await message.answer(
            "✅ Доступ уже открыт 👇",
            reply_markup=menu_keyboard()
        )
        return

    ok = await flyer.check(
        user_id=user_id,
        language_code=message.from_user.language_code,
    )

    if not ok:
        await message.answer(
            "⏳ Выполни задания и нажми кнопку ниже 👇",
            reply_markup=check_keyboard()
        )
        return

    await set_access_granted(user_id)
    await message.answer(
        "✅ Доступ открыт 👇",
        reply_markup=menu_keyboard()
    )


# ================= CHECK BUTTON =================
@dp.callback_query(F.data == "check_tasks")
async def check_tasks(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if await has_access(user_id):
        await callback.answer()
        await callback.message.answer(
            "✅ Доступ открыт 👇",
            reply_markup=menu_keyboard()
        )
        return

    ok = await flyer.check(
        user_id=user_id,
        language_code=callback.from_user.language_code,
    )

    if not ok:
        await callback.answer("❌ Задания ещё не выполнены", show_alert=True)
        return

    await set_access_granted(user_id)
    await callback.answer("✅ Готово!")
    await callback.message.answer(
        "✅ Доступ открыт 👇",
        reply_markup=menu_keyboard()
    )


# ================= BROADCAST =================
@dp.message(Command("broadcast"))
async def broadcast_start(message: types.Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = True
    await message.answer(
        "✉️ Отправь сообщение для рассылки\n\n"
        "❌ /cancel — отмена"
    )


@dp.message(Command("cancel"))
async def broadcast_cancel(message: types.Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = False
    await message.answer("❌ Рассылка отменена")


# ================= MAIN HANDLER =================
@dp.message()
async def handler(message: types.Message):
    global broadcast_mode

    # ----- РАССЫЛКА -----
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

    # ----- НИЧЕГО НЕ ЛОВИМ -----
    return


# ================= RUN =================
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
