import requests
# import matplotlib.pyplot as plt
from datetime import timedelta


# PLIK Z POPRZEDNIEJ LISTY - LISTY 4
# UZYSKANIE NOTOWAN Z API NBP

def _url(path):
    return 'http://api.nbp.pl/api/exchangerates/rates/' + path


def get_rates_avg_time(currency, from_date, to_date):
    """
    Getting rates for time frames with additional function
    If user passess more time than 365 days then program
    GETs from api more than once

    return: rates in dictionary format (rate[day] = rate in this day)
    """

    rates = {}

    # If time is longer than a year, get rates in partitions
    while (to_date - from_date).days >= 365:
        to_date_temp = from_date + timedelta(days=365)
        url = _url('/a/{0}/{1}/{2}'.format(currency, from_date.strftime("%Y-%m-%d"), to_date_temp.strftime("%Y-%m-%d")))
        resp = requests.get(url)

        if resp.status_code != 200:
            raise Exception("GET STATUS CODE: {0}".format(resp.status_code))

        for rate in resp.json()['rates']:
            rates[rate['effectiveDate']] = rate['mid']

        from_date = to_date_temp

    if from_date < to_date:
        url = _url('/a/{0}/{1}/{2}'.format(currency, from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
    resp = requests.get(url)

    if resp.status_code != 200:
        raise Exception("GET STATUS CODE: {0}".format(resp.status_code))

    for rate in resp.json()['rates']:
        rates[rate['effectiveDate']] = rate['mid']

    return rates

