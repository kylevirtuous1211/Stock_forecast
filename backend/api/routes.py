from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from backend.services.historical import fetch_historical_data

router = APIRouter()

class HistoricalRequest(BaseModel):
    symbols: List[str]
    lookback_minutes: int = 96
    end_time: datetime = None

@router.post("/historical", response_model=Dict[str, Any])
async def get_historical_data(request: HistoricalRequest):
    try:
        data = fetch_historical_data(request.symbols, request.lookback_minutes, request.end_time)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/tracked-stocks", response_model=List[str])
async def get_tracked_stocks():
    # symbols from model/fetch_sector_data.py
    symbols = ["XLK", "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "ADBE", "CRM", "AMD", "QCOM", "TXN"]
    return symbols

@router.get("/index-performance", response_model=Dict[str, Any])
async def get_index_performance(lookback_minutes: int = 60):
    try:
        # Fetch data for XLK
        data = fetch_historical_data(["XLK"], lookback_minutes)
        return {"data": data.get("XLK", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
