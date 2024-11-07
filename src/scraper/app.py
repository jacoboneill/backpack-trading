import calendar
import requests
import logging
import csv
import time
from datetime import datetime, timedelta


def get(ticker):
    url = f"https://api.nasdaq.com/api/quote/{ticker}/historical?assetclass=stocks&fromdate=2014-11-07&limit=9999&todate=2024-11-07"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0"
    }
    res = requests.get(url, headers=headers)
    time.sleep(1)
    if res.json()["status"]["rCode"] != 200:
        logging.error(
            f"Request for {ticker} failed with status code {res.json()['status']['rCode']}."
        )
        return None
    else:
        logging.info(f"Request for {ticker} complete.")
        return res.json()["data"]["tradesTable"]["rows"]


def parse_data(data, ticker):
    date = datetime.strptime(data["date"], "%m/%d/%Y")
    epoch = calendar.timegm(date.timetuple())

    open = float(data["open"][1:])
    close = float(data["close"][1:])
    price = (open + close) / 2

    result = {
        "ticker": ticker,
        "epoch": epoch,
        "price": price,
    }

    return result


if __name__ == "__main__":
    # Logging config
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # Scrape data from NASDAQ and parse
    data = []
    with open("./companies.csv", "r") as f:
        for ticker in f.read().splitlines():
            res = get(ticker)
            if res != None:
                for row in res:
                    data.append(parse_data(row, ticker))

    # Write to CSV file
    with open("./historic_data.csv", "w") as f:
        dict_writer = csv.DictWriter(f, data[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(data)
