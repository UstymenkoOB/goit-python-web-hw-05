from datetime import date, timedelta
import aiohttp
import asyncio
import platform

URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='
CURRENCY = ['USD', 'EUR', 'CHF', 'GBP',
            'PLZ', 'SEK', 'XAU', 'CAD']
curr_list = list()

async def main_exchange(date):
    url = URL + date
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            return result

def date_str(n):
    day = date.today() - timedelta(days=n)
    day_str = day.strftime("%d.%m.%Y")
    return day_str

def currency_list(currency, curr_list):
    for el in currency:
        if el.upper() in CURRENCY:
            curr_list.append(el.upper())
        else:
            print(el, '- there is no such currency')


async def exchange(arguments):
    n = 1
    data = list()
    try:
        if len(arguments) >= 2:
            n = int(arguments[1])
        if n > 10:
            print("The maximum number of days is 10")
            n = 10
    except ValueError:
        raise ValueError("Wrong arguments")

    if len(arguments) > 2:
        curr_list = ['USD', 'EUR']
        currency_list(arguments[2:], curr_list)
    else:
        curr_list = ['USD', 'EUR']
    
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    for i in range(n):
        data_day = dict()
        data_currency = dict()
        date_next = date_str(i)
        r = await main_exchange(date_next)
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

    return data

