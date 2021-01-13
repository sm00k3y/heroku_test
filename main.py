import stock_rates
import db_init
import api
from datetime import date

if __name__ == "__main__":

    from_date = date(2005, 12, 30)
    to_date = date(2008, 1, 1)

    db_init.init(from_date, to_date)

    api.run()

