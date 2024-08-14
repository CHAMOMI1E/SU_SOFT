import asyncio
import logging
import sys
from asyncio import sleep

from aiogram import types, F
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config.settings import BOT_KEY
from aiogram.filters import CommandStart

bot = Bot(BOT_KEY)
dp = Dispatcher()


async def is_registered(user_id):
    pass



@dp.message(CommandStart())
async def test(message: types.Message):
    await message.answer("test")
    user_id = message.from_user.id

    if await is_registered(user_id):
        await message.answer("Вы уже зарегистрированы!")
    else:
        await message.answer("Введите ключ для регистрации:")

        @dp.message(F.text)
        async def get_registration_key(msg: types.Message):
            registration_key = msg.text
            await register_user(user_id, registration_key)
            await msg.answer("Регистрация завершена! Теперь вы можете пользоваться ботом.")


async def background_task():
    while True:
        # Ваше действие здесь
        print("Фоновая задача выполняется каждые 15 минут.")
        await asyncio.sleep(7)


async def start_bot() -> None:
    asyncio.create_task(background_task())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s"
        "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
        stream=sys.stdout,
    )

    try:

        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Shutting down")
