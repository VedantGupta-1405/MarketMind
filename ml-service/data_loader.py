import yfinance as yf


STOCK_MAP = {
    1: "AAPL",
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
}


def fetch_stock_data(stock_id, start="2015-01-01", end="2024-01-01"):

    if stock_id not in STOCK_MAP:
        raise ValueError(f"Invalid stock_id: {stock_id}")

    ticker = STOCK_MAP[stock_id]

    try:
        data = yf.download(ticker, start=start, end=end)

        if data.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        if hasattr(data.columns, 'levels'):
            data.columns = [col[0] for col in data.columns]

        return data

    except Exception as e:
        raise RuntimeError(
            f"Error fetching data for {ticker}: {str(e)}"
        )