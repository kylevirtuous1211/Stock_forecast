import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

load_dotenv("backend/.env")

api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_API_SECRET")

print(f"Loaded Key: {api_key[:4]}****{api_key[-4:] if api_key else 'None'}")
print(f"Loaded Secret: {secret_key[:4]}****{secret_key[-4:] if secret_key else 'None'}")

if not api_key:
    print("Error: API Key is missing")
    exit(1)

client = StockHistoricalDataClient(api_key, secret_key, sandbox=True)
# print(help(StockHistoricalDataClient))


print("Attempting to fetch data...")
try:
    req = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Minute,
        start=datetime.utcnow() - timedelta(days=2),
        end=datetime.utcnow() - timedelta(days=1),
        # feed="iex" # Default to SIP
    )
    bars = client.get_stock_bars(req)
    print("Success!")
    print(bars.df.head())
except Exception as e:
    print("Failed!")
    print(e)
