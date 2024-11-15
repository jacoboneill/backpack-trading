from API import API
from Account import Account
from Portfolio import Portfolio
from TradingAlgorithm import TradingAlgorithm

if __name__ == "__main__":
    # Get access to data
    # api = API("../historic_data.db")
    api = API("../test.db")

    # Initalise timestamps
    timestamps = api.getTimestamps()

    # Initalise Portfolio and Bank
    bank = [Account(10_000, 0.1, Portfolio(api.getStocks(timestamps[0])))]

    # Loop through each account in bank account
    for account in bank:
        # Loop through each timestamp
        for timestamp in timestamps[1:]:
            # Initalise trading algorithm
            trading_algorithm = TradingAlgorithm(account)

            # Update all stocks in portfolio and run trading algorithm
            new_stocks = api.getStocks(timestamp)
            optimal_portfolio = trading_algorithm.unboundedKnapsack(new_stocks)

            # Update portfolio with new optimal portfolio
            account.portfolio.updatePortfolioWithTemplate(optimal_portfolio)

    # Print Summary
    print(
        f"""Trading Simulation Summary:
    - Initial balance: {account.initial_balance}
    - Budget Allocation: {account.budget_allocation}
    - Final balance: {account.cash}
    - Portfolio Value: {portfolio.value()}
    - Net Profit / Loss {account.value()}
    """
    )
