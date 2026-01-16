import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"❌ ENV переменная {name} НЕ задана")
    return value


BOT_TOKEN = require_env("8571962927:AAG_KEcFhL5LhhoZYk-bAbBNQ8MFqWO6WP4")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("✅ Бот запущен и работает")


async def main():
    logging.info("🤖 Запуск polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
