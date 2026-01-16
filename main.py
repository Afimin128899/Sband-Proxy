from aiogram import Bot, Dispatcher, executor, types

TOKEN = "ВАШ_BOT_TOKEN"
BOT_USERNAME = "IMYA_TVOEGO_BOTA"  # без @

# SOCKS5 прокси (твой)
SOCKS_SERVER = "193.124.133.42"
SOCKS_PORT = "58976"
SOCKS_USER = "VxWwEWV95B"
SOCKS_PASS = "ea2pSdiR8Y"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    socks_link = (
        f"https://t.me/socks?"
        f"server={SOCKS_SERVER}"
        f"&port={SOCKS_PORT}"
        f"&user={SOCKS_USER}"
        f"&pass={SOCKS_PASS}"
    )

    share_text = (
        "🚀 Telegram стал работать медленно?\n\n"
        "Подключи прокси за 1 клик — работает сразу 👌\n\n"
        f"👉 https://t.me/{BOT_USERNAME}"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(
            text="🔗 Подключить прокси",
            url=socks_link
        ),
        types.InlineKeyboardButton(
            text="👥 Поделиться с другом",
            switch_inline_query=share_text
        ),
        types.InlineKeyboardButton(
            text="❌ Как отключить",
            callback_data="disable_proxy"
        )
    )

    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Бот подключает SOCKS-прокси для Telegram.\n"
        "Данные и сообщения не читаются.",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data == "disable_proxy")
async def disable_proxy(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "❌ Чтобы отключить прокси:\n\n"
        "Настройки → Данные и память → Прокси → Отключить"
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
