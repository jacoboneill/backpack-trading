import pandas
import seaborn
import matplotlib.pyplot as pyplot
import sqlite3
import animation


@animation.wait("spinner")
def genPlot(dataframe, field, title, filepath):
    seaborn.lineplot(data=dataframe, x="timestamp", y=field, hue="account_number")
    pyplot.title(title)
    pyplot.savefig(filepath)
    pyplot.close()


def createPlot(field, title):
    query = f"""
    SELECT
    d.timestamp,
    d.account_number,
    CASE
        WHEN COUNT(d.{field}) = 1 THEN MAX(d.{field})
        ELSE AVG(d.{field})
    END AS {field}
    FROM data d
    GROUP BY d."timestamp", d.account_number;
    """
    conn = sqlite3.connect("./output.db")
    dataframe = pandas.read_sql_query(query, conn)

    print(f"{title} being generated")

    fp = f"./plots/{field}.png"
    genPlot(dataframe, field, title, fp)
    print(f"{title} saved to {fp}")


if __name__ == "__main__":
    createPlot("balance", "Balance over Time")
    createPlot("budget", "Budget over Time")
    createPlot("portfolio", "Portfolio's Value over Time")
    createPlot("profit_loss", "Profit and Loss over Time")
