import string
import aiohttp
from json import loads
from bs4 import BeautifulSoup
from aiogram import Dispatcher, Bot, executor, types
import aioschedule
import asyncio

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}


async def get_currency_binance() -> float:
    cookies = {
    'cid': 'fneU1LWK',
    'bnc-uuid': '272fa314-4e15-4b73-baed-e478ae535f57',
    'source': 'organic',
    'campaign': 'www.google.com',
    'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22183cac19b3d1ec-0ebd1158fc47138-97a2733-2073600-183cac19b3e5dd%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTgzY2FjMTliM2QxZWMtMGViZDExNThmYzQ3MTM4LTk3YTI3MzMtMjA3MzYwMC0xODNjYWMxOWIzZTVkZCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%22183cac19b3d1ec-0ebd1158fc47138-97a2733-2073600-183cac19b3e5dd%22%7D',
    'sajssdk_2015_cross_new_user': '1',
    'userPreferredCurrency': 'RUB_USD',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Oct+12+2022+11%3A25%3A57+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=6.34.0&isIABGlobal=false&hosts=&consentId=fc88d61a-56a7-435a-a20f-e90fe730c29e&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&geolocation=RU%3BMOW',
    'BNC_FV_KEY': '3309e06e2f37a127b17cd93fd33cfc1dc2bb42e2',
    'BNC_FV_KEY_EXPIRE': '1665575629602',
    'fiat-prefer-currency': 'RUB',
    'OptanonAlertBoxClosed': '2022-10-12T05:54:24.139Z',
    'lang': 'ru',
    'showBlockMarket': 'false',
    'sys_mob': 'no',
    'common_fiat': 'RUB',
    'videoViewed': 'yes',
}


    json_data = {
        'proMerchantAds': False,
        'page': 1,
        'rows': 10,
        'payTypes': [],
        'countries': [],
        'publisherType': None,
        'asset': 'USDT',
        'fiat': 'RUB',
        'tradeType': 'BUY',
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', cookies=cookies, headers=headers, json=json_data) as response:
            file = await response.json()
            binance_usdt = float(file["data"][0]["adv"]["price"])
    return binance_usdt


async def get_currency_unistream() -> float:
    params = {
    'destination': 'UZB',
    'amount': '9000000',
    'currency': 'UZS',
    'accepted_currency': 'RUB',
    'profile': 'client_context_brand',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://online.unistream.ru/card2cash/calculate', params=params, headers=headers) as response:
            file = await response.json()
            unistream_rub = float(file["fees"][0]["acceptedAmount"])
            unistream = 9000000 / unistream_rub
            unistream -= unistream * 0.008
    return unistream
        


async def get_currency_moex() -> float:
    url = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=USD_RUB'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
            moex_usd = soup.find(id='ctl00_PageContent_tbxCurrentRate').text.split()[2].replace(',', '.')
            
    return float(moex_usd) + float(moex_usd) * 0.015
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
    moex = await get_currency_moex()
    unistream = await get_currency_unistream()
    binance = await get_currency_binance()
    
    # print(koronapay_usd)
    # print(koronapay_eur)
    # print(koronapay_try)
    # print(get_currency_garantex())
    spread_usd = (max(garantex, koronapay_usd) - min(garantex, koronapay_usd)) / (max(garantex, koronapay_usd)) * 100
    spread_eur = (max(garantex, koronapay_eur) - min(garantex, koronapay_eur)) / (max(garantex, koronapay_eur)) * 100

    mess = f'Курс короны в турцию 🇹🇷 \n Доллар 💵 = {"{0:.2f}".format(koronapay_usd)} \n Евро 💶 = {"{0:.2f}".format(koronapay_eur)} \n Лира 💷 = {"{0:.2f}".format(koronapay_try)} \n Garantex USDT 💰 = {garantex} \n Binance USDT💰= {"{0:.2f}".format(binance)} \n Грязный спред по $ = {"{0:.2f}".format(spread_usd)}% \n Грязный спред по € = {"{0:.2f}".format(spread_eur)}% \n Закуп $ под SWIFT = {"{0:.2f}".format(moex)} \n  Спред SWIFT = 1.5% \n Unistream Узбекистан 🇺🇿 \n 1 RUB = {"{0:.2f}".format(unistream)}'
    return mess


async def send_messages() -> None:
    with open("config.txt", "r", encoding="utf-8") as f:
        user_id = f.read().strip().split("\n")[-1].strip()
        await bot.send_message(user_id, await main())


async def create_aioschedule() -> None:
    aioschedule.every(1).seconds.do(send_messages)

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
    
