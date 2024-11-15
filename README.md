# Dev Log

## 10-10-2024 12:37

I have decided as my final project for CS50x that I want to create a paper trading bot. To do this I have the idea to adapt the _unbounded knapsack problem's_ algorithm with inspirations of weights in AI development to come up with an adaptable software that can make choices on whether to buy or sell stocks with a budget. I want to use paper money to see if the concept works.

To do this, I have decided to use modularisation to organise the code and have the following classes:

| Class Name            | Description                                                                                                         |
|-----------------------|---------------------------------------------------------------------------------------------------------------------|
| `DatabaseConnection`  | Interact with the SQLite database to persist data of the stocks and bank.                                           |
| `DatabaseInitialiser` | A sublass of `DatabaseConnection` that includes methods to initialise the database. Used as a utility class.        |
| `StockAPI`            | An adapter class that will abstract the stock api, in this case finance.cs50.io                                     |
| `TradingAlgorithm`    | A stratergy class that will use the bounded knapsack algorithm to calculate the best portfolio at the current time. |
| `Bot`                 | The manager of the project, filled with static methods for the main loop                                            |

These classes will all be used in the `app.py` file to update everything once, and use a cron job to run the program periodically.

## 10-10-2024 13:27

I have created a flowchart for the overall program as well as the setup function:

### Overview

![Overview](./README_assets/flowchart_overview.png)

### Setup

![Setup](./README_assets/flowchart_setup.png)

## 10-10-2024 14:24

Created the flowchart for the main section, decided to further abstract it. I'm also adding a class `Bot` to manage all these things and run main

### Main

![Main](./README_assets/flowchart_main.png)

### Update Stock Data and Weights

![Update Stock Data and Weights](./README_assets/flowchart_update_stock_data_and_weights.png)

## 10-10-2024 15:36

After a lot of research and tinkering, I have been able to take an unbounded knapsack algorithm and make it so it will return to me the items that were picked for the heighest value given the budget for weight. The values are a bit the wrong way round as the `PRICE` would be the `weight` column, and the `WEIGHT` would be the `price` column.

### Code
```py
def uks_rec(BUDGET, STOCKS, INDEX):
    if INDEX == 0:
        count = BUDGET // STOCKS[0]["weight"]
        return (count * STOCKS[0]["price"], [STOCKS[0]["id"]] * count)

    not_take_val, not_take_items = uks_rec(BUDGET, STOCKS, INDEX - 1)

    take_val = float("-inf")
    take_items = []
    if STOCKS[INDEX]["weight"] <= BUDGET:
        take_val_recursive, take_items_recursive = uks_rec(
            BUDGET - STOCKS[INDEX]["weight"], STOCKS, INDEX
        )
        take_val = STOCKS[INDEX]["price"] + take_val_recursive
        take_items = [STOCKS[INDEX]["id"]] + take_items_recursive

    if take_val > not_take_val:
        return (take_val, take_items)
    else:
        return (not_take_val, not_take_items)


def uks(BUDGET, STOCKS):
    N = len(STOCKS)
    return uks_rec(BUDGET, STOCKS, N - 1)


if __name__ == "__main__":
    BUDGET = 100
    STOCKS = [
        {
            "id": 1,
            "price": 10,
            "weight": 5,
        },
        {
            "id": 2,
            "price": 30,
            "weight": 10,
        },
        {
            "id": 3,
            "price": 20,
            "weight": 15,
        },
    ]
    _, selected_items = uks(BUDGET, STOCKS)

    print("Stocks selected: ", selected_items)
```

### Output
```
Stocks selected:  [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
```

## 10-10-2024 16:05

I have finally added the update_portfolio section to the flow chart. Now I need to design and plan the Classes. I think I want to use UML diagrams for this so I can refer back to it while programming:

### Update Portfolio

![Update Portfolio](./README_assets/flowchart_update_portfolio.png)

## 11-10-2024 11:21

I have created the UML class diagram with all the methods and attributes as well as the relationships. I wish there was a way to import data from the database and make it all in objects, but I think this will be a waste of compute time in the long run and with python not having type checking, I don't see the point.

```mermaid
classDiagram
    class DatabaseConnection{
        -databaseURI
        -database
        -cursor
        -DatabaseConnection(databaseURI)
    }
    class DatabaseInitaliser{
        -database
        -bankSchema
        -stockSchema
        -transactionsSchema
        -companyNames
        +DatabaseInitaliser(databasePath, bankSchemaPath, stockSchemaPath, transactionsSchemaPath, companyNamesPath)
        -validateDatabase(database)
        -validateBankTable(bankSchema)
        -validateStockTable(stockSchema)
        -validateTransactionsTable(transactionsSchema)
        -importStockData(companyNames)
    }
    class SQLiteInitaliser
    class Database{
        +getAllStockData()
        +updateAllStockData(stockData)
        +getPortfolio()
        +getBalance()
        +updatePortfolio(currentPortfolio, newPortfolio)
        -addTransaction(stock)
    }
    class SQLite
    class StockAPI{
        +getStockValue(stockSymbol)$
        +buyStock(database, stockSymbol, value)$
        +sellStock(database, stockSymbol, value)$
    }
    class CS50StockAPI
    class TradingAlgorithm{
        -currentPortfolio
        -bankBalance
        -newPortfolio
        +TradingAlgorithm(currentPortfolio, bankBalance)
        +execute()
    }
    class UnboundedKnapsackAlgorithm
    class Bot{
        -database
        -stockAPI
        -tradingAlgorithm
        -inintaliaseDatabase
        +Bot(database, stockAPI, tradingAlgorithm, initaliseDatabase)
        -setup()
        -updateStockData()
        -getNewPortfolio()
        -updatePortfolio()
    }

    Bot o-- SQLiteInitaliser
    Bot o-- SQLite
    Bot o-- CS50StockAPI
    Bot o-- UnboundedKnapsackAlgorithm

    DatabaseConnection <|-- DatabaseInitaliser
    DatabaseConnection <|-- Database
    DatabaseInitaliser <|-- SQLiteInitaliser
    Database <|-- SQLite

    StockAPI <|-- CS50StockAPI

    TradingAlgorithm <|-- UnboundedKnapsackAlgorithm
```

## 11-10-2024 13:09

After doing some research using: [getting started with pytest (beginner - intermediate) anthony explains #518](https://www.youtube.com/watch?v=mzlH8lp4ISA) I have decided to use _pytest_ as my testing framework and the following file structure:
```sh
.
├── Dockerfile
├── LICENSE
├── src
│   ├── __init__.py
│   ├── bot.py
│   ├── database.py
│   ├── stock_api.py
│   └── trading_algorithm.py
└── tests
    ├── test_bot.py
    ├── test_database.py
    ├── test_stock_api.py
    └── test_trading_algorithm.py

3 directories, 11 files
```

This will give me a seperation of concerns for each class type. The next step is to setup the venv, which should be pretty easy.

For the venv, you use `python3 -m venv [dir for venv]`. This is pretty simple and then you can use `./bin/activate` to enter into the venv. The only thing I will be adding is the _pytest_ framework by using `pip3 install pytest` while inside the venv.

Once this is done, I will add the classes to implement.

## 11-10-2024 16:09

Been trying to setup testing and classes for the database, but couldn't figure out how to import the classes from `/src` into `/tests`. To solve this I created a `pyproject.toml` file and added the following:
```toml
[tool.pytest.ini_options]
pythonpath = [
    "src"
]
```

Thanks to __hoefling__ on [stack overflow](https://www.stackoverflow.com) for the [answer](https://www.stackoverflow.com/questions/50155464/using-pytest-with-a-src-layer#answer-50156706)

## 07-11-2024 12:33

Wow I haven't looked at this for a while... I have decided to do a quick proof of concept to make sure this idea works on a new branch `feature/proof-of-concept`. This will save me time from doing _ttd_ and actually get a working prototype.

As well as this, I joined a _Python_ discord server and asked them the best way to go about testing with a database. Thanks to their community I think the best way to go about it is to make a test database, but let's not get ahead of ourselves and actully make sure the idea works


## 07-11-2024 14:41

I finally created a scraper to get all the historic data for all the stocks I want to do. Here are the things I learnt:

- You can export SQL queries in the `sqlite3` program by doing the following (Thanks __gdw2__ on [stack overflow](https://stackoverflow.com/questions/6076984/sqlite-how-do-i-save-the-result-of-a-query-as-a-csv-file#answer-6077039)):
```sql
.mode csv
.output test.csv
SELECT * FROM table;
.output stdout
```

- There is a NASDAQ API for getting historic data that I used the FireFox dev tools network tab to be able to get the URL
![NASDAQ Network Tab](./README_assets/nasdaq_network_tab.png)
---
![NASDAQ API](./README_assets/nasdaq_api.png)

- You can use `datetime` and `timedelta` to create a range for the dates, so that everything lines up when you export the dict to a csv

- There is a logging library to make logging look nicer (I used this to log the scraping stage)

- Dictionary comprehension. It's like list comprehension, but for dicts (This one sounds silly but I didn't know about it until now and seems like a useful feature, but may not be KISS friendly...)

Here is the output when I did the scrape:
```sh
07-11-2024 14:52:06 - [INFO] Request for WMT complete.
07-11-2024 14:52:08 - [INFO] Request for AMZN complete.
07-11-2024 14:52:09 - [INFO] Request for AAPL complete.
07-11-2024 14:52:10 - [INFO] Request for UNH complete.
07-11-2024 14:52:11 - [INFO] Request for CVS complete.
07-11-2024 14:52:12 - [INFO] Request for XOM complete.
07-11-2024 14:52:13 - [INFO] Request for SHEL complete.
07-11-2024 14:52:15 - [INFO] Request for TM complete.
07-11-2024 14:52:18 - [INFO] Request for MCK complete.
07-11-2024 14:52:19 - [INFO] Request for GOOG complete.
07-11-2024 14:52:20 - [INFO] Request for COR complete.
07-11-2024 14:52:21 - [INFO] Request for COST complete.
07-11-2024 14:52:22 - [INFO] Request for JPM complete.
07-11-2024 14:52:24 - [INFO] Request for TTE complete.
07-11-2024 14:52:25 - [INFO] Request for BP complete.
07-11-2024 14:52:26 - [INFO] Request for MSFT complete.
07-11-2024 14:52:27 - [INFO] Request for CAH complete.
07-11-2024 14:52:29 - [INFO] Request for STLA complete.
07-11-2024 14:52:31 - [INFO] Request for CVX complete.
07-11-2024 14:52:32 - [INFO] Request for CI complete.
07-11-2024 14:52:33 - [INFO] Request for F complete.
07-11-2024 14:52:34 - [INFO] Request for BAC complete.
07-11-2024 14:52:36 - [INFO] Request for GM complete.
07-11-2024 14:52:37 - [INFO] Request for ELV complete.
07-11-2024 14:52:38 - [INFO] Request for C complete.
07-11-2024 14:52:39 - [INFO] Request for CNC complete.
07-11-2024 14:52:41 - [INFO] Request for JD complete.
07-11-2024 14:52:42 - [INFO] Request for HD complete.
07-11-2024 14:52:44 - [INFO] Request for MPC complete.
07-11-2024 14:52:45 - [INFO] Request for KR complete.
07-11-2024 14:52:46 - [INFO] Request for PSX complete.
07-11-2024 14:52:48 - [INFO] Request for HMC complete.
07-11-2024 14:52:49 - [INFO] Request for WBA complete.
07-11-2024 14:52:50 - [INFO] Request for VLO complete.
07-11-2024 14:52:51 - [INFO] Request for SAN complete.
07-11-2024 14:52:54 - [INFO] Request for MUFG complete.
07-11-2024 14:52:55 - [INFO] Request for META complete.
07-11-2024 14:52:56 - [INFO] Request for HSBC complete.
07-11-2024 14:52:57 - [INFO] Request for VZ complete.
07-11-2024 14:52:58 - [INFO] Request for BABA complete.
07-11-2024 14:53:00 - [INFO] Request for T complete.
07-11-2024 14:53:01 - [INFO] Request for CMCSA complete.
07-11-2024 14:53:02 - [INFO] Request for WFC complete.
07-11-2024 14:53:05 - [INFO] Request for NCV complete.
07-11-2024 14:53:06 - [INFO] Request for GS complete.
07-11-2024 14:53:07 - [INFO] Request for TGT complete.
07-11-2024 14:53:08 - [INFO] Request for EQNR complete.
07-11-2024 14:53:09 - [INFO] Request for HUM complete.
07-11-2024 14:53:11 - [INFO] Request for ENIC complete.
07-11-2024 14:53:12 - [INFO] Request for E complete.
07-11-2024 14:53:13 - [INFO] Request for PBR complete.
07-11-2024 14:53:14 - [INFO] Request for SWKS complete.
07-11-2024 14:53:17 - [INFO] Request for TSLA complete.
07-11-2024 14:53:18 - [INFO] Request for MS complete.
07-11-2024 14:53:19 - [INFO] Request for BEP complete.
07-11-2024 14:53:20 - [INFO] Request for JNJ complete.
07-11-2024 14:53:22 - [INFO] Request for ADM complete.
07-11-2024 14:53:23 - [INFO] Request for SMFG complete.
07-11-2024 14:53:24 - [INFO] Request for PEP complete.
07-11-2024 14:53:25 - [INFO] Request for UPS complete.
07-11-2024 14:53:26 - [INFO] Request for AXTA complete.
07-11-2024 14:53:29 - [INFO] Request for FDX complete.
07-11-2024 14:53:30 - [INFO] Request for SONY complete.
07-11-2024 14:53:31 - [INFO] Request for DIS complete.
07-11-2024 14:53:32 - [INFO] Request for DELL complete.
07-11-2024 14:53:33 - [INFO] Request for RY complete.
07-11-2024 14:53:35 - [INFO] Request for LOW complete.
07-11-2024 14:53:36 - [INFO] Request for BYD complete.
07-11-2024 14:53:37 - [INFO] Request for MUFG complete.
07-11-2024 14:53:38 - [INFO] Request for PG complete.
07-11-2024 14:53:41 - [INFO] Request for ACI complete.
07-11-2024 14:53:42 - [INFO] Request for ET complete.
07-11-2024 14:53:43 - [INFO] Request for BA complete.
07-11-2024 14:53:44 - [INFO] Request for SYY complete.
07-11-2024 14:53:45 - [INFO] Request for VINP complete.
07-11-2024 14:53:47 - [INFO] Request for TD complete.
07-11-2024 14:53:48 - [INFO] Request for JBSS complete.
07-11-2024 14:53:49 - [INFO] Request for UBS complete.
07-11-2024 14:53:50 - [INFO] Request for TSM complete.
07-11-2024 14:53:52 - [INFO] Request for RTX complete.
07-11-2024 14:53:53 - [INFO] Request for ITUB complete.
07-11-2024 14:53:54 - [INFO] Request for MT complete.
07-11-2024 14:53:55 - [INFO] Request for GE complete.
07-11-2024 14:53:57 - [INFO] Request for LMT complete.
07-11-2024 14:53:58 - [INFO] Request for AXP complete.
07-11-2024 14:53:59 - [INFO] Request for CAT complete.
07-11-2024 14:54:00 - [INFO] Request for BBVA complete.
07-11-2024 14:54:01 - [INFO] Request for KEP complete.
07-11-2024 14:54:04 - [INFO] Request for MET complete.
07-11-2024 14:54:05 - [INFO] Request for AEON complete.
07-11-2024 14:54:06 - [INFO] Request for LYG complete.
07-11-2024 14:54:07 - [INFO] Request for DB complete.
07-11-2024 14:54:08 - [INFO] Request for HCA complete.
07-11-2024 14:54:10 - [INFO] Request for SMFG complete.
07-11-2024 14:54:11 - [INFO] Request for UL complete.
07-11-2024 14:54:12 - [INFO] Request for ACN complete.
07-11-2024 14:54:13 - [INFO] Request for BCS complete.
07-11-2024 14:54:16 - [INFO] Request for PGR complete.
07-11-2024 14:54:17 - [INFO] Request for IBM complete.
07-11-2024 14:54:18 - [INFO] Request for DE complete.
07-11-2024 14:54:19 - [INFO] Request for NVDA complete.
07-11-2024 14:54:20 - [INFO] Request for SNEX complete.
07-11-2024 14:54:22 - [INFO] Request for MFG complete.
07-11-2024 14:54:23 - [INFO] Request for ING complete.
07-11-2024 14:54:24 - [INFO] Request for MRK complete.
07-11-2024 14:54:25 - [INFO] Request for BG complete.
07-11-2024 14:54:27 - [INFO] Request for BUD complete.
07-11-2024 14:54:28 - [INFO] Request for PKX complete.
07-11-2024 14:54:29 - [INFO] Request for COP complete.
07-11-2024 14:54:31 - [INFO] Request for PFE complete.
07-11-2024 14:54:32 - [INFO] Request for DAL complete.
07-11-2024 14:54:33 - [INFO] Request for SNX complete.
07-11-2024 14:54:34 - [INFO] Request for ALL complete.
07-11-2024 14:54:35 - [INFO] Request for CSCO complete.
07-11-2024 14:54:36 - [INFO] Request for BBD complete.
07-11-2024 14:54:39 - [INFO] Request for CHTR complete.
07-11-2024 14:54:40 - [INFO] Request for ABBV complete.
07-11-2024 14:54:41 - [INFO] Request for INTC complete.
07-11-2024 14:54:42 - [INFO] Request for TJX complete.
07-11-2024 14:54:44 - [INFO] Request for NVS complete.
07-11-2024 14:54:45 - [INFO] Request for RIO complete.
07-11-2024 14:54:46 - [INFO] Request for PRU complete.
07-11-2024 14:54:47 - [INFO] Request for BHP complete.
07-11-2024 14:54:48 - [INFO] Request for HP complete.
07-11-2024 14:54:51 - [INFO] Request for UAL complete.
07-11-2024 14:54:52 - [INFO] Request for PFGC complete.
07-11-2024 14:54:53 - [INFO] Request for TSN complete.
07-11-2024 14:54:54 - [INFO] Request for AAL complete.
07-11-2024 14:54:55 - [INFO] Request for BNS complete.
07-11-2024 14:54:56 - [INFO] Request for NKE complete.
07-11-2024 14:54:58 - [INFO] Request for BMO complete.
07-11-2024 14:54:59 - [INFO] Request for KB complete.
07-11-2024 14:55:00 - [INFO] Request for SNY complete.
07-11-2024 14:55:03 - [INFO] Request for ORCL complete.
07-11-2024 14:55:04 - [INFO] Request for CB complete.
07-11-2024 14:55:05 - [INFO] Request for EPD complete.
07-11-2024 14:55:06 - [INFO] Request for COF complete.
07-11-2024 14:55:07 - [INFO] Request for HDB complete.
07-11-2024 14:55:09 - [INFO] Request for VOD complete.
07-11-2024 14:55:10 - [INFO] Request for PAGP complete.
07-11-2024 14:55:11 - [INFO] Request for SMFG complete.
07-11-2024 14:55:12 - [INFO] Request for WKC complete.
07-11-2024 14:55:14 - [ERROR] Request for ORAN failed with status code 400.
07-11-2024 14:55:16 - [INFO] Request for AIG complete.
07-11-2024 14:55:17 - [INFO] Request for AMX complete.
07-11-2024 14:55:20 - [INFO] Request for AZN complete.
07-11-2024 14:55:22 - [INFO] Request for KO complete.
07-11-2024 14:55:24 - [INFO] Request for CHSCO complete.
07-11-2024 14:55:27 - [INFO] Request for BMY complete.
07-11-2024 14:55:29 - [INFO] Request for TY complete.
07-11-2024 14:55:31 - [INFO] Request for DOW complete.
07-11-2024 14:55:33 - [INFO] Request for FMX complete.
07-11-2024 14:55:34 - [INFO] Request for TEF complete.
07-11-2024 14:55:38 - [INFO] Request for BBY complete.
07-11-2024 14:55:40 - [INFO] Request for TMO complete.
07-11-2024 14:55:41 - [INFO] Request for MGA complete.
07-11-2024 14:55:43 - [INFO] Request for GD complete.
07-11-2024 14:55:45 - [INFO] Request for VALE complete.
07-11-2024 14:55:47 - [INFO] Request for TRV complete.
07-11-2024 14:55:50 - [INFO] Request for WBD complete.
07-11-2024 14:55:52 - [INFO] Request for CM complete.
07-11-2024 14:55:54 - [INFO] Request for LYB complete.
07-11-2024 14:55:56 - [INFO] Request for USB complete.
07-11-2024 14:55:57 - [INFO] Request for ABT complete.
07-11-2024 14:55:59 - [INFO] Request for NOC complete.
07-11-2024 14:56:03 - [INFO] Request for DG complete.
07-11-2024 14:56:05 - [INFO] Request for CVE complete.
07-11-2024 14:56:07 - [ERROR] Request for ACST failed with status code 400.
07-11-2024 14:56:08 - [INFO] Request for COOP complete.
07-11-2024 14:56:11 - [INFO] Request for PBF complete.
07-11-2024 14:56:14 - [INFO] Request for GSK complete.
07-11-2024 14:56:16 - [INFO] Request for SU complete.
07-11-2024 14:56:18 - [INFO] Request for UBER complete.
07-11-2024 14:56:20 - [INFO] Request for HON complete.
07-11-2024 14:56:21 - [INFO] Request for MDLZ complete.
07-11-2024 14:56:23 - [INFO] Request for SBUX complete.
07-11-2024 14:56:26 - [INFO] Request for QCOM complete.
07-11-2024 14:56:28 - [INFO] Request for AVGO complete.
07-11-2024 14:56:29 - [INFO] Request for USFD complete.
07-11-2024 14:56:31 - [INFO] Request for DHI complete.
07-11-2024 14:56:33 - [INFO] Request for PM complete.
07-11-2024 14:56:35 - [INFO] Request for PCAR complete.
07-11-2024 14:56:37 - [INFO] Request for PDD complete.
07-11-2024 14:56:39 - [INFO] Request for CRH complete.
07-11-2024 14:56:41 - [INFO] Request for CRM complete.
07-11-2024 14:56:43 - [INFO] Request for NUE complete.
07-11-2024 14:56:44 - [INFO] Request for JBL complete.
07-11-2024 14:56:46 - [INFO] Request for SAP complete.
07-11-2024 14:56:49 - [INFO] Request for LEN complete.
07-11-2024 14:56:51 - [INFO] Request for LLY complete.
07-11-2024 14:56:53 - [INFO] Request for MOH complete.
07-11-2024 14:56:54 - [INFO] Request for CMI complete.
07-11-2024 14:56:56 - [INFO] Request for BTI complete.
07-11-2024 14:56:58 - [INFO] Request for BK complete.
07-11-2024 14:57:01 - [INFO] Request for NFLX complete.
07-11-2024 14:57:05 - [INFO] Request for NVO complete.
07-11-2024 14:57:06 - [INFO] Request for TFC complete.
07-11-2024 14:57:08 - [INFO] Request for SLB complete.
07-11-2024 14:57:09 - [INFO] Request for EC complete.
07-11-2024 14:57:12 - [INFO] Request for ARW complete.
07-11-2024 14:57:14 - [INFO] Request for LIN complete.
07-11-2024 14:57:15 - [INFO] Request for MMM complete.
07-11-2024 14:57:17 - [INFO] Request for V complete.
07-11-2024 14:57:19 - [INFO] Request for APO complete.
07-11-2024 14:57:20 - [INFO] Request for ENB complete.
07-11-2024 14:57:22 - [INFO] Request for ABBV complete.
```

Which is a lot, and some didn't work (even though they do on the _finance.cs50.io_ API), but is a good starting point for me to get a POC

Finally, like they did in the CS50 SQL lecture, I imported all this data into a `.db` file so I can make queries on it later.

```sql
.mode csv stocks
.import historic_data stocks

SELECT * FROM stocks;
```

This showed that all the data was imported with the following schema:
```
CREATE TABLE IF NOT EXISTS "stocks"(
"ticker" TEXT, "datetime" TEXT, "price" TEXT);
```

## 07-11-2024 20:32

So I had to go and do some things, which means there was a big break between this update. During this time I did some research on whether I want to use an ORM, specifically SQLAlchemy, or just RAW SQL to interact with the database, and after careful consideration, I decided to just use RAW SQL for at least the POC. I decided this because, to be honest, I already know how to use it, which means I can develop quickly.

My plan is to use SQL, and not Python, to get the weights and then finally compute it in Python. I think this will be good practice for my RAW SQL.

In the meanwhile, I found out that SQLite doesn't support date objects, so instead of creating another script to update the date time objects in the db to epoch, I would add it to the scraper.

### References
[Raw SQL or ORM](https://www.youtube.com/watch?v=x1fCJ7sUXCM)
[datetime to EPOCH](https://www.geeksforgeeks.org/convert-python-datetime-to-epoch/)

## 07-11-2024 20:51

Final thing of the day, probably... I made it so there was a symlink for the database in the root of the `src` dir. I did this so the output of the file was always in the `scraper` dir. Simply for organisation. Apart from that the scraper seems to be working really well and I think that I have all the data I need to test my theory on!

## 08-11-2024 16:10

New day, new challenge. I've got all the data so I guess the final solution is to implement the algorithm. I think I want to implement it simmilarly to the plan I have, but instead of saving the bank state, and keeping a history. Originally I was going to load the data in dynamically as this is the biggest dataset I have worked on, however I then realised the database, as it stands, is currently only 12MB, and I have more than enough space in RAM to do that. Therefore, I will be doing:

```py
cur.execute(sql_query)
data = cur.fetchall()
```

instead of the alternative:

```py
for row in cur.execute(sql_query):
    ...
```

For the setup I will need to do the following:

1. Get all the distinct epoch's in an array to loop over: `SELECT DISTINCT s.epoch FROM stocks s;`
2. Create a dictionary with key values of the ticker and the following schema:
```
ticker: {
    weight: int,
    transactions: [
        {
            price: real,
            time: int
        },
        ...
    ]
}
```
3. Create a dictionary for the bank, that will include the cash balance, and portfolio value:
```
bank = [
    {
        cash: real,
        budget: int
        portfolio: [
            {
            ticker: string,
            price: real,
            time: real,
            },
            ...
        ]
    },
    ...
]
```
4. Fill in the first set of weights as the value normalised, so:
$$\frac{\text{value} - \min_\text{global}}{\max_\text{global} - \min_\text{global}}$$

For the loop, I will do the following:

1. Loop from the second epoch
2. Get all values in that epoch with their tickers: `SELECT s.ticker, s.price FROM stocks s WHERE s.epoch = ?`
3. Get all values from the epoch before with the same query
3. Get the max and min of the values: `SELECT MAX(s.price), MIN(s.price) FROM stocks s WHERE s.epoch = ?`
4. Loop through all the tickers to get their weights with the following: 
$$\frac{(\text{value}_i - \text{value}_{i-1}) - \min_\text{global}}{\max_\text{global} - \min_\text{global}}$$
5. Use the knapsack algorithm to decide which stocks to have in the portfolio, with a range of percentages for the budget
6. Update the bank with the current values, buy and sell stocks where needed and update cash

## 10-11-2024 12:22

Back again, I have decided against this idea, instead taking a more OOP plan as I am getting cofused on what I am doing. Therefore I will have the following:


### Bot
- A utility class with static methods only, and no state. A manager if you will
    - Get current stocks from `API`
    - Calculate optimum portfolio
    - Request update to `Account`
    - Have it's own dict with `ticker` as key, and: `previous price`, `new_price`, and `weight` as a dict:
    ```
    {
        previous_price: real,
        new_price: real,
        weight: real
    }
    ```

### Bank
- An aggregator of Accounts, which has `CRUD` functionality for `Account`'s
```
bank = list(Account)
```

#### Account
- A dict with `cash`, `budget`, a `Portfolio` object, and a `History` object
```
account = {
    cash: real,
    budget: real,
    portfolio: Portfolio,
    history: History
}
```

##### Portfolio
- A dict with key value pairs of a `ticker` and a dict with `price`, `quantity`, and epoch `timestamp`
```
{
    price: real,
    quantity: int,
    timestamp: int
}
```

##### History
- A list with dicts of `ticker`, `price`, `quantity`, and epoch `timestamp`
```
{
    ticker: string,
    price: real,
    quantity: int,
    timestamp: int
}
```

### API
- A utility class that allows access to the database
- Get next timestamp from current using `SQL`
- Get stocks at timestamp
- Get max and min price from timestamp

## 15-11-2024 09:18

So I tried to implement all the classes above, and many of them worked, with a few adjustments of course, but the main issue I am having is that the call stack allocation is being exceeded. I'm not entireley suprised by this, even with memoisation the amount of different branches is going to exceed Python's recurssion limit:

```
sys.setrecursionlimit(limit)

Set the maximum depth of the Python interpreter stack to limit. This limit prevents infinite recursion from causing an overflow of the C stack and crashing Python.

The highest possible limit is platform-dependent. A user may need to set the limit higher when they have a program that requires deep recursion and a platform that supports a higher limit. This should be done with care, because a too-high limit can lead to a crash.

If the new limit is too low at the current recursion depth, a RecursionError exception is raised.

Changed in version 3.5.1: A RecursionError exception is now raised if the new limit is too low at the current recursion depth.
```

Therefore, I am having to take a little side quest into algorithms, to understand the dynamic programming approach. I used ChatGPT to generate a curriculum for me, and have been watching YouTube content on the subjects and then doing programming challenges based on what I have learned. Here is what I have so far:

1. [x] Develop Understanding of Recursion
2. [ ] Introduction to Greedy Algorithms & Problem Solving Patterns
3. [ ] Introduction to Dynamic Programming Concepts 
4. [ ] Mastering 0/1 Knapsack as Preparation for Unbounded Knapsack
5. [ ] Learn and Implement the Unbounded Knapsack Solution

For 1, I learned how recurssion can work using CS50's short on it, with the challenege of writing a recurssive function to show the collatz conjecture.

```py
def collatz(n, steps=0):
    if n < 1 or n % 1 != 0:
        raise TypeError(f"n must be a positive integer: {n}")

    if n == 1:
        return steps

    if n % 2 == 0:
        return collatz(n / 2, steps=steps + 1)

    if n % 2 != 0:
        return collatz((3 * n) + 1, steps=steps + 1)
```

I then went further, by creating a second function to incorporate memoisation, with the help of another YouTube video

```py
def collatzMemo(n, memo=dict(), steps=0):
    if n < 1 or n % 1 != 0:
        raise TypeError(f"n must be a positive integer: {n}")

    if n == 1:
        return steps

    if n in memo:
        return steps + memo[n]

    if n % 2 == 0:
        result = collatzMemo(n / 2, memo=memo, steps=steps + 1)

    if n % 2 != 0:
        result = collatzMemo((3 * n) + 1, memo=memo, steps=steps + 1)

    memo[n] = result - steps
    return result
```

Finally, I wrote a test function to time how long the function takes, given a range of values:
```py
def test(func, repeats):
    start = time.time()
    for i in range(1, repeats):
        func(i)
    return time.time() - start
```

and ran it in a `if main` clause:
```py
if __name__ == "__main__":
    n = 100_000

    print(f"no memo: {test(collatz, n)}")

    print(f"   memo: {test(collatzMemo, n)}")
```

This was the result:
```stdout
no memo: 3.719251871109009
   memo: 0.17868900299072266
```

As you can see, the memoisation function runs almost **22** times faster!

## 15-11-2024 18:36

I finally did number 2:

> [x] Introduction to Greedy Algorithms & Problem Solving Patterns

And followed [this](https://www.youtube.com/watch?v=lfQvPHGtu6Q) video, and used what I learned to solve the fractional knapsack problem. After many attempts where I failed to figure out how to loop and have the last value be added fractionally, I looked up the solution. However, I understand how all of this works:

```py
def fractional_knapsack(capacity: int, items: list[dict[str, int | float]]) -> dict[str, int]:
    for item in items:
        item["ratio"] = item["value"] / item["size"]

    items.sort(key=lambda i: i["ratio"], reverse=True)

    bag = list()
    total_value = 0
    current_weight = 0
    for item in items:
        if current_weight + item["size"] <= capacity:
            total_value += item["value"]
            bag.append(item)
            current_weight += item["size"]
        else:
            fraction = (capacity - current_weight) / item["size"]
            value = item["value"] * fraction
            total_value += value
            bag.append({"index": item["index"], "size": fraction, "value": value})
            break

    return {"value": total_value, "items": bag}


if __name__ == "__main__":

    capacity = 25
    items = [
        {"index": 0, "size": 22, "value": 19},
        {"index": 1, "size": 10, "value": 9},
        {"index": 2, "size": 9, "value": 9},
        {"index": 3, "size": 7, "value": 6},
    ]

    print(fractional_knapsack(capacity, items))

```

I learnt a lot while making this, most notably however the `list.sort(key=)` keyword parameter, as well as `lambda` functions. This made it much easier to sort it all, instead of using the solutions way of using a set and memorising the way the set is laid out.
