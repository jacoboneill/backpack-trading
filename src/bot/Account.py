class Account:
    def __init__(self, cash, budget_allocation, portfolio):
        self.initial_balance = cash
        self.cash = cash
        self.budget_allocation = budget_allocation
        self._generate_budget()
        self.portfolio = portfolio

    def _generate_budget(self):
        self.budget = self.cash * self.budget_allocation

    def _deposit(self, cash):
        self.cash += cash
        self._generate_budget()

    def _withdraw(self, cash):
        if self.cash - cash < 0:
            raise Exception(f"Trying to withdraw {cash} out of balance: {self.cash}")

        self.cash -= cash
        self._generate_budget()

    def sellStock(self, stock, quantity):
        sell_price = quantity * self.portfolio[stock]["price"]
        self.portfolio[stock]["quantity"] -= quantity
        self._deposit(sell_price)

    def buyStock(self, stock, quantity):
        buy_price = quantity * self.portfolio[stock]["price"]
        self.portfolio[stock]["quantity"] += quantity
        self._withdraw(buy_price)

    def updatePortfolioWithTemplate(self, template):
        for portfolio in self.portfolio:
            portfolio_quantity = portfolio["quantity"]

            if portfolio in template:
                template_quantity = template["quantity"]

                if portfolio_quantity > template_quantity:
                    self.sellStock(portfolio, portfolio_quantity - template_quantity)
                elif portfolio_quantity < template_quantity:
                    self.buyStock(portfolio, template_quantity - portfolio_quantity)
            elif portfolio_quantity > 0:
                self.sellStock(portfolio, portfolio_quantity)

    def value(self):
        return (self.cash + self.portfolio.value()) - self.initial_balance
