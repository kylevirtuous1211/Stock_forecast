import os
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")

if not ALPACA_API_KEY or not ALPACA_API_SECRET:
    raise ValueError("Alpaca API credentials not found in environment variables")

client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_API_SECRET, sandbox=True)

def fetch_historical_data(symbols: List[str], lookback_minutes: int = 96, end_time: datetime = None) -> Dict[str, List[Dict]]:
    """
    Fetches historical bars for the given symbols.
    """
    if end_time is None:
        end_time = datetime.utcnow()
    # Fetch a bit more to ensure we have enough after alignment/filling
    start_time = end_time - timedelta(minutes=lookback_minutes * 2) 

    request_params = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Minute,
        start=start_time,
        end=end_time
    )

    bars = client.get_stock_bars(request_params)
    
    # Convert to DataFrame
    df = bars.df
    
    result = {}
    
    if df.empty:
        for symbol in symbols:
            result[symbol] = []
        return result

    # Reset index to access symbol and timestamp columns if they are in the index
    # Standard alpaca-py response has MultiIndex (symbol, timestamp)
    if 'symbol' not in df.columns and 'symbol' in df.index.names:
        df = df.reset_index(level='symbol')
    
    # Also reset timestamp if needed
    if 'timestamp' not in df.columns and 'timestamp' in df.index.names:
        df = df.reset_index(level='timestamp')
        
    # Ensure symbol column exists
    if 'symbol' not in df.columns:
        # Fallback or error? If query was for single symbol and index has no name?
        # Typically single symbol query might have just timestamp index?
        if len(symbols) == 1 and 'symbol' not in df.columns:
             df['symbol'] = symbols[0]
    
    for symbol in symbols:
        if 'symbol' in df.columns:
            symbol_data = df[df['symbol'] == symbol].copy()
            # Convert timestamp to string for JSON serialization
            if 'timestamp' in symbol_data.columns:
                symbol_data['timestamp'] = symbol_data['timestamp'].apply(lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x))
            result[symbol] = symbol_data.to_dict(orient="records")
        else:
            result[symbol] = []
            
    return result

def align_data(data: Dict[str, List[Dict]], fill_method: str = "ffill") -> pd.DataFrame:
    """
    Aligns multiple stock series into a single DataFrame with a shared timestamp index.
    Fills missing values using the specified method (default: forward fill).
    """
    dfs = []
    for symbol, records in data.items():
        if not records:
            continue
        df = pd.DataFrame(records)
        if 'timestamp' not in df.columns:
            continue
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        # Keep only numeric columns + symbol? Or just close price?
        # User said "Align these stocks into a single matrix". 
        # Usually for PatchTST we need multivariate series.
        # Let's keep all columns but prefix with symbol, or use MultiIndex columns.
        # MultiIndex columns (symbol, feature) is best.
        df.columns = pd.MultiIndex.from_product([[symbol], df.columns])
        dfs.append(df)
    
    if not dfs:
        return pd.DataFrame()
        
    # Join all dataframes on the index
    # outer join to include all timestamps, then fill
    aligned_df = pd.concat(dfs, axis=1, join="outer").sort_index()
    
    # Forward fill to handle missing data (e.g. one stock didn't trade in a minute)
    if fill_method == "ffill":
        aligned_df.ffill(inplace=True)
        # Backward fill initial gaps if any
        aligned_df.bfill(inplace=True)
        
    return aligned_df
