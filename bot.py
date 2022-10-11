from aiogram import Dispatcher, Bot, executor, types
import config
import aioschedule
import asyncio


bot = Bot(token = config.token)
dp = Dispatcher(bot)


async def send_messages():
    await bot.send_message(config.id, "JSA")

async def create_aioschedule() -> None:
    aioschedule.every(2).seconds.do(send_messages)
    
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(0.5)


async def create_tasks(message: types.Message):
    tasks = [
        create_aioschedule()
    ]
    
    await asyncio.gather(*tasks)

executor.start_polling(dp, on_startup=create_tasks)
