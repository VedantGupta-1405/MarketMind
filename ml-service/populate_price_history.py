import requests
import yfinance as yf

BACKEND_URL = "http://localhost:8080"

STOCK_MAP = {
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
}

START_DATE = "2015-01-01"
END_DATE = "2024-01-01"


def fetch_existing_history(stock_id):
    response = requests.get(
        f"{BACKEND_URL}/price-history/{stock_id}",
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def fetch_stock_data(ticker):
    data = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        raise RuntimeError(
            f"No data returned for {ticker}"
        )

    if hasattr(data.columns, "levels"):
        data.columns = [
            column[0]
            for column in data.columns
        ]

    return data


def save_price_history(stock_id, ticker, data):
    saved = 0

    for index, row in data.iterrows():
        date = index.strftime("%Y-%m-%d")

        open_price = float(row["Open"])
        close_price = float(row["Close"])
        high = float(row["High"])
        low = float(row["Low"])
        volume = int(row["Volume"])

        payload = {
            "date": date,
            "openPrice": open_price,
            "closePrice": close_price,
            "high": high,
            "low": low,
            "volume": volume
        }

        response = requests.post(
            f"{BACKEND_URL}/price-history/{stock_id}",
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        saved += 1

        if saved % 100 == 0:
            print(
                f"{ticker}: {saved} records saved"
            )

    return saved


def main():
    for stock_id, ticker in STOCK_MAP.items():
        print(
            f"\nProcessing {ticker} "
            f"(stock ID {stock_id})..."
        )

        existing = fetch_existing_history(
            stock_id
        )

        if existing:
            print(
                f"{ticker} already has "
                f"{len(existing)} price-history records. Skipping."
            )
            continue

        print(
            f"Downloading {ticker} historical data..."
        )

        data = fetch_stock_data(ticker)

        print(
            f"Downloaded {len(data)} records for {ticker}"
        )

        saved = save_price_history(
            stock_id,
            ticker,
            data
        )

        print(
            f"{ticker}: {saved} records inserted"
        )

    print("\nPrice history population completed.")


if __name__ == "__main__":
    main()