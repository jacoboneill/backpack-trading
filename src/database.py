import sqlite3

class SQLiteConnection:
    self._databaseURI
    self._database
    self._cursor

    def __init__(self, databaseURI):
        self._databaseURI = databaseURI
        self._connect()

    def _connect(self, databaseURI):
        self._database = sqlite3.connect(self._databaseURI)
        self._database.row_factory = sqlite3.Row
        self._cursor = self._database.cursor()

    def __del__(self):
        self._cursor.close()
        self._database.close()

class SQLiteInitaliser(SQLiteConnection):
    self._bankSchemaPath
    self._stockSchemaPath
    self._transactionsSchemaPath
    self._companyNamesPath

    def __init__(self, databaseURI, bankSchemaPath, stockSchemaPath, transactionsSchemaPath, companyNamesPath):
        super().__init__(databaseURI)
        self._bankSchemaPath = bankSchemaPath
        self._stockSchemaPath = stockSchemaPath
        self._transactionsSchemaPath = transactionsSchemaPath
        self._companyNamesPath = companyNamesPath

    def initialise(self):
        self._validateDatabase(self._databaseURI)
        self._validateBankTable(self._bankSchemaPath)
        self._validateStockTable(self._stockSchemaPath)
        self._validateTransactionsTable(self._transactionsSchemaPath)
        self._importStockData(self._companyNamesPath)

    def _validateDatabase(self, database):
        pass

    def _validateBankTable(self, bankSchemaPath):
        pass

    def _validateStockTable(self, stockSchemaPath):
        pass

    def _validateTransactionsTable(self, transactionsSchemaPath):
        pass

    def _importStockData(self, companyNamesPath):
        pass

class SQLite(SQLiteConnection):
    def __init__(self, databaseURI):
        super().__init__(databaseURI)

    def getAllStockData():
        pass

    def updateAllStockData(stockData):
        pass

    def getPortfolio():
        pass

    def getBalance():
        pass

    def updatePortfolio(currentPortfolio, newPortfolio):
        pass

    _addTransaction(stock):
        pass
