import psycopg2
import db_init
from db_config import config
from datetime import datetime, date

OK = 200
WRONG_DATE_FORMAT = 400
WRONG_DATE_RANGE = 416
NO_DATA_FOUND = 404


def get_rates_day(date_string):
    # Check if date format is ok
    err_code = check_date(date_string, db_init.RANGE_START_DATE, db_init.RANGE_END_DATE)
    if err_code != OK:
        return [], err_code

    # Select date from database
    command = "SELECT date, rate, interpolated FROM PLN_EXCHANGE_RATES WHERE date = '{}'".format(date_string)  #.strftime("%Y-%m-%d"))
    transactions = execute_command(command)

    # Check for no data found
    if transactions == []:
        return [], NO_DATA_FOUND

    return transactions, OK


def get_rates_dates(date_from, date_to):
    err_code = check_dates(date_from, date_to, db_init.RANGE_START_DATE, db_init.RANGE_END_DATE)
    if err_code != OK:
        return [], err_code

    command = "SELECT date, rate, interpolated FROM PLN_EXCHANGE_RATES WHERE date >= '{}' AND date <= '{}'".format(date_from, date_to)
    transactions = execute_command(command)
    
    if transactions == []:
        return transactions, NO_DATA_FOUND

    return transactions, OK


def get_sales_date(date_string):
    err_code = check_date(date_string, db_init.RANGE_START_DATE, db_init.RANGE_END_DATE)
    if err_code != OK:
        return [], err_code

    command = """ SELECT DATE(payment_date), SUM(amount), rate
                  FROM payment LEFT JOIN PLN_EXCHANGE_RATES ON DATE(payment_date) = date
                  WHERE DATE(payment_date) = '{}'
                  GROUP BY DATE(payment_date), PLN_EXCHANGE_RATES.rate
                  ORDER BY DATE(payment_date) DESC""".format(date_string)
    transactions = execute_command(command)

    if transactions == []:
        return transactions, NO_DATA_FOUND

    return transactions, OK


def get_sales_dates(date_from, date_to):
    err_code = check_dates(date_from, date_to, db_init.RANGE_START_DATE, db_init.RANGE_END_DATE)
    if err_code != OK:
        return [], err_code

    command = """ SELECT DATE(payment_date), SUM(amount), rate
                  FROM payment LEFT JOIN PLN_EXCHANGE_RATES ON DATE(payment_date) = date
                  WHERE DATE(payment_date) >= '{}' AND DATE(payment_date) <= '{}'
                  GROUP BY DATE(payment_date), PLN_EXCHANGE_RATES.rate
                  ORDER BY DATE(payment_date) DESC""".format(date_from, date_to)
    transactions = execute_command(command)

    if transactions == []:
        return transactions, WRONG_DATE_RANGE

    return transactions, OK


## HELPER FUNCTIONS ##

def check_date(date_string, start_date, end_date):
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        return WRONG_DATE_FORMAT

    if date < start_date or date > end_date:
        return WRONG_DATE_RANGE

    return OK


def check_dates(date_from, date_to, start_date, end_date):
    try:
        date1 = datetime.strptime(date_from, "%Y-%m-%d").date()
        date2 = datetime.strptime(date_to, "%Y-%m-%d").date()
    except ValueError:
        return WRONG_DATE_FORMAT

    if date1 < start_date or date1 > end_date or date2 < start_date or date2 > end_date:
        return WRONG_DATE_RANGE

    return OK


def execute_command(command):
    """ Executes command in the DVDRENTAL database """
    transactions = []
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        cur.execute(command)

        records = cur.fetchall()

        for row in range(0, len(records)):
            transactions.append(records[row])

        cur.close()

    except (Exception, psycopg2.DatabaseError) as err:
        print(err)

    finally:
        if conn is not None:
            conn.close()

    return transactions

