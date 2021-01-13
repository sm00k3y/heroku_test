import flask
import db_handler
import db_init
from flask import jsonify
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cache import Cache


app = flask.Flask(__name__)
app.config['DEBUG'] = True

cache = Cache()

limiter = Limiter(
        app,
        key_func=get_remote_address,  # limits requests per user
        default_limits=['200 per day', '50 per hour']
        )


@app.route('/')
def home_page():
    return """<CENTER><H1>API - lista 5</H1>
              <H2>Jakub Smolka - 246987</H2>
              <H3>GitHub - Jake S</H3></CENTER>"""


@app.route('/USD/<date_string>', methods=['GET'])
@limiter.limit('10 per minute')
def get_rate_date(date_string):
    json_obj = {}

    if cache.has_rate(date_string):
        return jsonify(cache.rates_by_day[date_string]), db_handler.OK

    transactions, err_code = db_handler.get_rates_day(date_string)

    if err_code != db_handler.OK:
        json_obj = err_msg(err_code)
    else:
        json_obj[transactions[0][0].strftime("%Y-%m-%d")] = {'rate': float(transactions[0][1]), 'interpolated': transactions[0][2]}
        cache.rates_by_day[date_string] = json_obj

    return jsonify(json_obj), err_code


@app.route('/USD/<date_from>/<date_to>', methods=['GET'])
@limiter.limit('10 per minute')
def get_rates_dates(date_from, date_to):
    json_obj = {}
    
    if cache.has_rates_range(date_from, date_to):
        return cache.get_rates_range(date_from, date_to), db_handler.OK

    transactions, err_code = db_handler.get_rates_dates(date_from, date_to)

    if err_code != db_handler.OK:
        json_obj = err_msg(err_code)
    else:
        for triple in transactions:
            str_date = triple[0].strftime("%Y-%m-%d")
            json_obj[str_date] = {'rate': float(triple[1]), 'interpolated': triple[2]}
            cache.rates_by_day[str_date] = json_obj[str_date]

    return jsonify(json_obj), err_code


@app.route('/sales/<date_string>', methods=['GET'])
@limiter.limit('5 per minute')
def get_sales_date(date_string):
    json_obj = {}

    if cache.has_sale(date_string):
        return jsonify(cache.sales_by_day[date_string]), db_handler.OK

    transactions, err_code = db_handler.get_sales_date(date_string)

    if err_code != db_handler.OK:
        json_obj = err_msg(err_code)
    else:
        data = transactions[0]
        json_obj[data[0].strftime("%Y-%m-%d")] = {
                'sum_of_sales_in_USD': round(float(data[1]), 2),
                'sum_of_sales_in_PLN': round(float(data[1] * data[2]), 2),
                'USD_to_PLN_rate': float(data[2])}
        cache.sales_by_day[date_string] = json_obj

    return jsonify(json_obj), err_code


@app.route('/sales/<date_from>/<date_to>', methods=['GET'])
@limiter.limit('1 per minute')
def get_sales_dates(date_from, date_to):
    json_obj = {}
    transactions, err_code = db_handler.get_sales_dates(date_from, date_to)

    if err_code != db_handler.OK:
        json_obj = err_msg(err_code)
    else:
        for triple in transactions:
            json_obj[triple[0].strftime("%Y-%m-%d")] = {
                    'sum_of_sales_in_USD': round(float(triple[1]), 2),
                    'sum_of_sales_in_PLN': round(float(triple[1] * triple[2]), 2),
                    'USD_to_PLN_rate': float(triple[2])}

    return jsonify(json_obj), err_code


def err_msg(err_code):
    json_obj = {}
    cache.check_refresh()  # Checks for refresh every time a query is done

    if err_code == db_handler.WRONG_DATE_FORMAT:
        json_obj['ERROR'] = 'You entered a wrong date format. Correct date format is: YYYY-MM-DD'
    elif err_code == db_handler.WRONG_DATE_RANGE:
        json_obj['ERROR'] = 'Date is out of range. The range is {} - {}'.format(db_init.RANGE_START_DATE, db_init.RANGE_END_DATE)
    elif err_code == db_handler.NO_DATA_FOUND:
        json_obj['ERROR'] = 'No data found for given range of dates'
    
    return json_obj


def run():
    app.run()

