import requests
import csv
import time
from datetime import datetime, timedelta

def get(ticker):
    url = f"https://api.nasdaq.com/api/quote/{ticker}/historical?assetclass=stocks&fromdate=2014-11-07&limit=9999&todate=2024-11-07"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0"
    }
    res = requests.get(url, headers=headers)
    return res.json()["data"]["tradesTable"]["rows"]
    time.sleep(1)

def parse_data(data):
    # Convert data to hashmap of date to average price
    parsed_hashmap = {datetime.strptime(i["date"], "%m/%d/%Y"): (float(i["open"][1:]) + float(i["close"][1:])) / 2 for i in data}

    # Fill data in from 10 years ago to today
    end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=(3653))

    parsed_data = {start + timedelta(days=i): parsed_hashmap[start + timedelta(days=i)] if start + timedelta(days=i) in parsed_hashmap else None for i in range((end - start).days + 1)}
    parsed_data["ticker"] = ticker

    return parsed_data
    

data = []
with open("./companies.csv", "r") as f:
    ticker = "AAPL"
    data.append(parse_data(get(ticker)))

with open("./historic_data.csv", "w") as f:
    dict_writer = csv.DictWriter(f, data[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(data)
