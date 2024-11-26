from datetime import datetime
import sqlite3

def databaseInit(filepath):
    conn = sqlite3.connect("./output.db")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS data;")
    cur.execute("""
        CREATE TABLE data (
            account_number REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            balance REAL NOT NULL,
            budget REAL NOT NULL,
            portfolio REAL NOT NULL,
            profit_loss REAL NOT NULL
        );
    """)

    return (conn, cur)


if __name__ == "__main__":
    # Create Database
    conn, cur = databaseInit("./output.db")

    # Load log into memory, easier than chunking
    lines = []
    with open("./poc.log", "r") as log_file:
        lines = [l.strip() for l in log_file.readlines()]

    # Increment through log, add to database
    while lines:
        timestamp = int(datetime.strptime(lines[0], "%d-%m-%Y").timestamp())
        for i in range(3):
            offset = 7 * i
            data = {
                "account_number": i + 1,
                "timestamp": timestamp,
                "balance": float(lines[offset + 3].split("$")[1]),
                "budget": float(lines[offset + 4].split("$")[1]),
                "portfolio": float(lines[offset + 5].split("$")[1]),
                "profit_loss": float(lines[offset + 6].split(": ")[1][:-1]),
            }

            cur.execute(
                "INSERT INTO data (account_number, timestamp, balance, budget, portfolio, profit_loss) VALUES(:account_number, :timestamp, :balance, :budget, :portfolio, :profit_loss)",
                data,
            )
            conn.commit()
            print(f"{lines[0]} Added to database")
        lines = lines[22:]
