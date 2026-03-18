from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.services.historical import fetch_historical_data
import asyncio
import random  # For mock recommendations until DB is fully wired
import time

router = APIRouter()

# Global state for training progress (In a real app, use Redis/Celery)
training_status = {
    "is_training": False,
    "progress": 0,
    "message": "Idle"
}

def mock_training_task():
    """Simulates a background training job."""
    global training_status
    training_status["is_training"] = True
    
    steps = [
        (10, "Fetching new data from Alpaca..."),
        (30, "Preprocessing 2 years of data..."),
        (50, "Finetuning Timer model (Epoch 1/5)..."),
        (70, "Finetuning Timer model (Epoch 3/5)..."),
        (90, "Saving new .pth model weights..."),
        (100, "Idle")
    ]
    
    for progress, msg in steps:
        training_status["progress"] = progress
        training_status["message"] = msg
        time.sleep(3) # Simulate work
        
    training_status["is_training"] = False

class OrderRequest(BaseModel):
    symbol: str
    quantity: float
    side: str = "buy" # or "sell"

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
        data = fetch_historical_data(["XLK"], lookback_minutes)
        return {"data": data.get("XLK", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==== Phase 2 Endpoints ====

@router.post("/retrain", status_code=202)
async def start_retraining(background_tasks: BackgroundTasks):
    global training_status
    if training_status["is_training"]:
        return {"status": "Already training", "message": training_status["message"]}
    
    background_tasks.add_task(mock_training_task)
    return {"status": "Accepted", "message": "Retraining job started in the background."}

@router.get("/train-status")
async def get_train_status():
    return training_status

@router.get("/recommendation")
async def get_recommendation(symbol: str = "AAPL"):
    # In a real app, query `inference_logs` table
    # For now, return a mock recommendation based on the symbol
    signals = ["BUY", "SELL", "HOLD"]
    # Seed random for consistent mock data per symbol for demo
    random.seed(sum(ord(c) for c in symbol) + int(time.time() / 60)) 
    
    return {
        "symbol": symbol,
        "signal": random.choice(["BUY", "BUY", "HOLD", "SELL"]), # Bias towards action
        "confidence": round(random.uniform(0.65, 0.98), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/order")
async def execute_order(request: OrderRequest):
    # Here you would use alpaca.create_order
    # Example:
    # client.submit_order(
    #     symbol=request.symbol,
    #     qty=request.quantity,
    #     side=request.side,
    #     type="market",
    #     time_in_force="day"
    # )
    
    # Mocking order execution
    return {
        "status": "success",
        "alpaca_order_id": f"mock_{int(time.time())}",
        "message": f"Successfully placed market {request.side} order for {request.quantity} shares of {request.symbol}."
    }
