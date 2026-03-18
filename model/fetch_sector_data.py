import os
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_API_SECRET")

if not api_key or not secret_key:
    raise ValueError("Alpaca API keys not found in environment variables")

client = StockHistoricalDataClient(api_key, secret_key, url_override=None, sandbox=True)

# XLK + Top 10 Holdings
symbols = ["XLK", "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "AMD", "QCOM", "TXN"]

print(f"Fetching data for: {symbols}")

# 1 year of data for faster testing (can change to 5 years later)
end_date = datetime.now()
start_date = end_date - timedelta(days=365) # 1 year

print(f"Fetching data for: {symbols} from {start_date} to {end_date}")

# Chunking by month to avoid timeouts/large memory usage
current_start = start_date
all_dfs = []

while current_start < end_date:
    current_end = current_start + timedelta(days=30)
    if current_end > end_date:
        current_end = end_date
    
    print(f"Fetching {current_start} to {current_end}...")
    
    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Minute,
            start=current_start,
            end=current_end,
            feed="iex"
        )
        
        bars = client.get_stock_bars(request_params)
        if not bars.df.empty:
            df_chunk = bars.df.reset_index()
            # Pivot
            df_pivot_chunk = df_chunk.pivot(index='timestamp', columns='symbol', values='close')
            all_dfs.append(df_pivot_chunk)
            print(f"Got {len(df_pivot_chunk)} rows")
        else:
            print("No data for chunk")
            
    except Exception as e:
        print(f"Error fetching chunk: {e}")
        
    current_start = current_end
    
if all_dfs:
    df_pivot = pd.concat(all_dfs)
    df_pivot.sort_index(inplace=True)
    # Forward fill missing data
    df_pivot = df_pivot.ffill().bfill()

    print(f"Data shape: {df_pivot.shape}")
    print(df_pivot.head())

    # Save to CSV
    output_path = "model/sector_data.csv"
    df_pivot.to_csv(output_path)
    print(f"Saved data to {output_path}")
else:
    print("No data fetched.")
