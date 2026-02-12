from backend.services.historical import align_data
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def test_alignment():
    # Mock data
    t1 = datetime.utcnow()
    t2 = t1 - timedelta(minutes=1)
    t3 = t1 - timedelta(minutes=2)
    
    data = {
        "AAPL": [
            {"timestamp": t3, "close": 150.0, "volume": 100},
            {"timestamp": t2, "close": 151.0, "volume": 110},
            {"timestamp": t1, "close": 152.0, "volume": 120}
        ],
        "MSFT": [
            # MSFT missing t2
            {"timestamp": t3, "close": 300.0, "volume": 500},
            {"timestamp": t1, "close": 305.0, "volume": 520}
        ]
    }
    
    print("Aligning data...")
    aligned = align_data(data)
    print("Aligned DataFrame:")
    print(aligned)
    
    # Check if t2 exists for MSFT (should be ffilled from t3)
    msft_t2_close = aligned.loc[t2, ("MSFT", "close")]
    print(f"MSFT close at t2 (filled): {msft_t2_close}")
    
    assert msft_t2_close == 300.0, f"Expected 300.0, got {msft_t2_close}"
    print("Alignment Logic Verified!")

if __name__ == "__main__":
    test_alignment()
