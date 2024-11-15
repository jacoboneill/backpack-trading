class API:
    def __init__(self, uri):
        import sqlite3

        self.conn = sqlite3.connect(uri)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def getTimestamps(self):
        self.cur.execute("SELECT DISTINCT s.epoch FROM stocks s;")
        timestamps = [i["epoch"] for i in self.cur.fetchall()]
        return timestamps

    def getStocks(self, timestamp):
        self.cur.execute(
            "SELECT s.ticker, s.price FROM stocks s WHERE s.epoch = ?", (timestamp,)
        )
        return self.cur.fetchall()
