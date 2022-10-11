import string
import aiohttp
from json import loads

from aiogram import Dispatcher, Bot, executor, types
import aioschedule
import asyncio

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}


async def get_currency_koronapay() -> list:
    url = "https://koronapay.com/transfers/online/api/transfers/tariffs"

    params = {
        "sendingCountryId": "RUS",
        "sendingCurrencyId": 810,
        "receivingCountryId": "TUR",
        "receivingCurrencyId": None,
        "paymentMethod": "debitCard",
        "receivingAmount": 500,
        "receivingMethod": "cash",
        "paidNotificationEnabled": "true"
    }

    currency_dict = {
        "USD": 840,
        "EUR": 978,
        "TRY": 949
    }

    currencies_values = []
    for currency_name in currency_dict.keys():
        params["receivingCurrencyId"] = currency_dict[currency_name]
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                response = await response.json()

            currencies_values.append(response[0]["exchangeRate"])
            await asyncio.sleep(1)

    return currencies_values


async def get_currency_garantex() -> float:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://garantex.io/trading/usdtrub", headers=headers) as response:
            response = await response.text()
            data = loads(response[response.find("//<![CDATA[") + 11:response.find("//]]>")]
                         .strip().strip("window.gon = ").strip(";"))

    # with open("data.json", "w", encoding="utf-8") as f:
    #     dump(data, f, indent=4, ensure_ascii=False)

    garantex_usd = float(data["tickers"]["usdtrub"]["sell"])
    return garantex_usd


async def main() -> string:
    koronapay_usd, koronapay_eur, koronapay_try = await get_currency_koronapay()
    garantex = await get_currency_garantex()
    # print(koronapay_usd)
    # print(koronapay_eur)
    # print(koronapay_try)
    # print(get_currency_garantex())
    spread_usd = (max(garantex, koronapay_usd) - min(garantex, koronapay_usd)) / (max(garantex, koronapay_usd)) * 100
    spread_eur = (max(garantex, koronapay_eur) - min(garantex, koronapay_eur)) / (max(garantex, koronapay_eur)) * 100

    mess = f'Курс короны в турцию 🇹🇷 \n Доллар 💵 = {"{0:.2f}".format(koronapay_usd)} \n Евро 💶 = {"{0:.2f}".format(koronapay_eur)} \n Лира 💷 = {"{0:.2f}".format(koronapay_try)} \n Garantex USDT 💰 = {garantex} \n Грязный спред по $ = {"{0:.2f}".format(spread_usd)}% \n Грязный спред по € = {"{0:.2f}".format(spread_eur)}%'
    return mess


async def send_messages() -> None:
    with open("config.txt", "r", encoding="utf-8") as f:
        user_id = f.read().strip().split("\n")[-1].strip()
        await bot.send_message(user_id, await main())


async def create_aioschedule() -> None:
    aioschedule.every(3).seconds.do(send_messages)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(0.5)


async def create_tasks(message: types.Message):
    tasks = [
        create_aioschedule()
    ]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    with open("config.txt", "r", encoding="utf-8") as f:
        token = f.read().strip().split("\n")[0].strip()
        bot = Bot(token=token)
    dp = Dispatcher(bot)

    executor.start_polling(dp, on_startup=create_tasks)
