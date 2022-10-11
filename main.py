import string
import requests
from time import sleep
from json import loads, dump

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}


def get_currency_koronapay() -> list:
    url = "https://koronapay.com/transfers/online/api/transfers/tariffs"

    params = {
        "sendingCountryId": "RUS",
        "sendingCurrencyId": 810,
        "receivingCountryId": "TUR",
        "receivingCurrencyId": None,
        "paymentMethod": "debitCard",
        "receivingAmount": 500,
        "receivingMethod": "cash",
        "paidNotificationEnabled": True
    }

    currency_dict = {
        "USD": 840,
        "EUR": 978,
        "TRY": 949
    }

    currencies_values = []
    for currency_name in currency_dict.keys():
        params["receivingCurrencyId"] = currency_dict[currency_name]
        response = requests.get(url, headers=headers, params=params).json()

        currencies_values.append(response[0]["exchangeRate"])
        sleep(1)

    return currencies_values


def get_currency_garantex() -> float:
    response = requests.get("https://garantex.io/trading/usdtrub", headers=headers).text
    data = loads(response[response.find("//<![CDATA[") + 11:response.find("//]]>")]
                 .strip().strip("window.gon = ").strip(";"))

    with open("data.json", "w", encoding="utf-8") as f:
        dump(data, f, indent=4, ensure_ascii=False)

    garantex_usd = float(data["tickers"]["usdtrub"]["sell"])
    return garantex_usd


def main() -> string:
    koronapay_usd, koronapay_eur, koronapay_try = get_currency_koronapay()
    garantex = get_currency_garantex()
    # print(koronapay_usd)
    # print(koronapay_eur)
    # print(koronapay_try)
    # print(get_currency_garantex())
    spread_usd = (max(garantex, koronapay_usd) - min(garantex, koronapay_usd)) / (max(garantex, koronapay_usd)) * 100
    spread_eur = (max(garantex, koronapay_eur) - min(garantex, koronapay_eur)) / (max(garantex, koronapay_eur)) * 100
    
    
    mess = f'Курс короны в турцию 🇹🇷 \n Доллар 💵 = {"{0:.2f}".format(koronapay_usd)} \n Евро 💶 = {"{0:.2f}".format(koronapay_eur)} \n Лира 💷 = {"{0:.2f}".format(koronapay_try)} \n Garantex USDT 💰 = {garantex} \n Грязный спред по $ = {"{0:.2f}".format(spread_usd)}% \n Грязный спред по € = {"{0:.2f}".format(spread_eur)}%'
    return mess

if __name__ == '__main__':
    main()