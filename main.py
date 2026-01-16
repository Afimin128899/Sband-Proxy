
import asyncio
import json
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

from flyerapi import Flyer
from aiohttp import web

logging.basicConfig(level=logging.INFO)

# ================= ENV =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FLYER_API_KEY = os.environ.get("FLYER_API_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))
PORT = int(os.environ.get("PORT", 10000))

# ================= FILE STORAGE =================
USERS_FILE = Path("users.json")

# ================= PROXY =================
SOCKS_SERVER = "193.124.133.42"
SOCKS_PORT = "58976"
SOCKS_USER = "VxWwEWV95B"
SOCKS_PASS = "ea2pSdiR8Y"

BOT_USERNAME = "Sband_Proxy_Bot"

# ================= INIT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
flyer = Flyer(FLYER_API_KEY)

broadcast_mode = False


# ================= FILE FUNCTIONS =================
def load_users():
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_user(user_id: int):
    users = load_users()
    users.setdefault(str(user_id), {"access": False})
    save_users(users)


def has_access(user_id: int) -> bool:
    users = load_users()
    return users.get(str(user_id), {}).get("access", False)


def set_access(user_id: int):
    users = load_users()
    users[str(user_id)] = {"access": True}
    save_users(users)


def get_all_users():
    users = load_users()
    return [int(uid) for uid in users.keys()]


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
            [InlineKeyboardButton(text="🔗 Подключить прокси", url=socks_link)],
            [InlineKeyboardButton(text="👥 Поделиться", switch_inline_query=share_text)],
        ]
    )


def check_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Проверить задания", callback_data="check_tasks")]
        ]
    )


# ================= HTTP KEEP-ALIVE =================
async def healthcheck(request):
    return web.Response(text="OK")


async def start_http():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()


# ================= START =================
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    add_user(user_id)

    if has_access(user_id):
        await message.answer("✅ Доступ открыт 👇", reply_markup=menu_keyboard())
        return

    ok = await flyer.check(
        user_id=user_id,
        language_code=message.from_user.language_code,
    )

    if not ok:
        await message.answer(
            "⏳ Выполни задания и нажми кнопку ниже 👇",
            reply_markup=check_keyboard(),
        )
        return

    set_access(user_id)
    await message.answer("✅ Доступ открыт 👇", reply_markup=menu_keyboard())


# ================= CHECK TASKS =================
@dp.callback_query(F.data == "check_tasks")
async def check_tasks(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if has_access(user_id):
        await callback.answer()
        await callback.message.answer("✅ Доступ открыт 👇", reply_markup=menu_keyboard())
        return

    ok = await flyer.check(
        user_id=user_id,
        language_code=callback.from_user.language_code,
    )

    if not ok:
        await callback.answer("❌ Задания ещё не выполнены", show_alert=True)
        return

    set_access(user_id)
    await callback.answer("✅ Готово!")
    await callback.message.answer("✅ Доступ открыт 👇", reply_markup=menu_keyboard())


# ================= EXPORT USERS =================
@dp.message(Command("export_users"))
async def export_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not USERS_FILE.exists():
        await message.answer("❌ users.json не найден")
        return

    await message.answer_document(
        FSInputFile(USERS_FILE),
        caption="📦 users.json"
    )


# ================= BROADCAST =================
@dp.message(Command("broadcast"))
async def broadcast_start(message: types.Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = True
    await message.answer(
        "✉️ Отправь сообщение для рассылки\n\n❌ /cancel — отмена"
    )


@dp.message(Command("cancel"))
async def broadcast_cancel(message: types.Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = False
    await message.answer("❌ Рассылка отменена")


@dp.message()
async def handler(message: types.Message):
    global broadcast_mode

    if broadcast_mode and message.from_user.id == ADMIN_ID:
        users = get_all_users()
        sent, failed = 0, 0

        for uid in users:
            try:
                await message.copy_to(uid)
                sent += 1
            except:
                failed += 1

        broadcast_mode = False
        await message.answer(
            f"✅ Рассылка завершена\n📤 Отправлено: {sent}\n❌ Ошибок: {failed}"
        )


# ================= RUN =================
async def main():
    if not USERS_FILE.exists():
        save_users({})

    await start_http()      # keep-alive для Render
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
