class Stock:
    def __init__(self, ticker: str, price: float) -> None:
        self.ticker: str = ticker
        self.price: float = price

    def __repr__(self):
        return repr(self.__dict__)
