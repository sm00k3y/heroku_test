from datetime import timedelta, datetime 
import time


# Simple cache mechanism that checks if a user query was made before and
# if yes, then returns that query
# if no, saves the query to a dict
# Every 24 hours cache clears itslef

class Cache():
    rates_by_day = {}
    sales_by_day = {}
    refresh_time = 86400  # 24h
    time_start = time.time()

    def __init__(self):
        time_start = time.time()

    def has_rate(self, date):
        return date in self.rates_by_day

    def has_rates_range(self, date_from, date_to):
        has = True
        delta = timedelta(days=1)
        tmp_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        tmp_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        while tmp_from <= tmp_to:
            if tmp_from.strftime("%Y-%m-%d") not in self.rates_by_day:
                has = False
            tmp_from += delta
        return has

    def has_sale(self, date):
        return date in self.sales_by_day

    def get_rates_range(self, date_from, date_to):
        ret_json = {}
        delta = timedelta(days=1)
        tmp_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        tmp_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        while tmp_from <= tmp_to:
            ret_json[tmp_from.strftime("%Y-%m-%d")] = self.rates_by_day[tmp_from.strftime("%Y-%m-%d")]
            tmp_from += delta
        return ret_json

    # Cache clears itself every 24 hours
    def check_refresh(self):
        if time.time() - self.time_start > self.refresh_time:
            rates_by_day = {}
            sales_by_day = {}
            time_start = time.time()

