import requests
import time
import sys
from datetime import datetime, timedelta

def wait_for_server(url, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Server is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
        print("Waiting for server...")
    return False

def test_historical():
    base_url = "http://127.0.0.1:8000"
    if not wait_for_server(f"{base_url}/api/health", timeout=120): # Increased timeout for installation
        print("Server failed to start.")
        sys.exit(1)

    # Use a hardcoded time known to be market hours (Tuesday Feb 10, 2026, 15:00 UTC)
    end_time = datetime(2026, 2, 10, 15, 0, 0)
    
    payload = {
        "symbols": ["AAPL", "MSFT"],
        "lookback_minutes": 10,
        "end_time": end_time.isoformat()
    }
    try:
        response = requests.post(f"{base_url}/api/historical", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Success! Data received:")
            # Print a snippet to verify structure
            for symbol, records in data["data"].items():
                print(f"{symbol}: {len(records)} records found.")
                if records:
                    print(f"Sample: {records[0]}")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_historical()
