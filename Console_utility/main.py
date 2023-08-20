from datetime import date, timedelta
import json
import aiohttp
import asyncio
import platform
import pprint
import sys

URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='
CURRENCY = ['USD', 'EUR', 'CHF', 'GBP',
            'PLZ', 'SEK', 'XAU', 'CAD']
curr_list = ['USD', 'EUR']

async def main(date):
    url = URL + date
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # print("Status:", response.status)
            # print("Content-type:", response.headers['content-type'])
            # print('Cookies: ', response.cookies)
            # print(response.ok)
            result = await response.json()
            return result

def date_str(n):
    day = date.today() - timedelta(days=n)
    day_str = day.strftime("%d.%m.%Y")
    return day_str

def currency_list(currency):
    for el in currency:
        if el.upper() in CURRENCY:
            curr_list.append(el.upper())
        else:
            print(el, '- there is no such currency')


if __name__ == "__main__":
    arguments = sys.argv
    n = 1
    data = list()
    try:
        if len(arguments) >= 2:
            n = int(arguments[1])
        if n > 10:
            print("The maximum number of days is 10")
            n = 10
    except ValueError:
        print("Wrong arguments")
        exit()

    if len(arguments) > 2:
        currency_list(arguments[2:])

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    for i in range(n):
        data_day = dict()
        data_currency = dict()
        date_next = date_str(i)
        r = asyncio.run(main(date_next))
        if 'error' in r.values():
            print(r['message'])
        else:
            exchange_rate = r['exchangeRate']
            for el in exchange_rate:
                rate = dict()
                for curr in curr_list:
                    if el["currency"] == curr:
                        rate['sale'] = el['saleRate']
                        rate['purchase'] = el['purchaseRate']
                        data_currency[curr] = rate
            data_day[date_next] = data_currency
            data.append(data_day)

    pprint.pprint(data)
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
