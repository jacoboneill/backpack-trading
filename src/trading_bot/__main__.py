from bank import Bank
from portfolio import Portfolio
from api import API
from tradingAlgorithm import TradingAlgorithm

def convertEpochToString(epoch: int) -> str:
    from time import strftime, localtime
    return strftime('%d-%m-%Y', localtime(epoch))

if __name__ == "__main__":
    # Setup
    bank = Bank()
    bank.addAccount(10_000, 0.1)
    bank.addAccount(10_000, 0.25)
    bank.addAccount(10_000, 0.5)

    api = API("../historic_data.db")
    for account in bank.accounts:
        account.updateStockHistory(api.getStocks(api.timestamps[0]))

    # Main Loop
    for timestamp in api.timestamps[1:]:
        new_stocks = api.getStocks(timestamp)
        for account in bank.accounts:
            old_stocks, _ = account.updateStockHistory(new_stocks)
            optimal_portfolio = TradingAlgorithm(old_stocks.stocks, new_stocks.stocks).getOptimalPortfolio(account.budget)
            account.rebalanceAccount(optimal_portfolio)
            
            log = f"{convertEpochToString(timestamp)}\n{bank}"
            with open("./sim.log", "a") as log_file:
                log_file.write(log)

            print(log)
