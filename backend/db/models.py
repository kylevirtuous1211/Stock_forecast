from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, BigInt
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class InferenceLog(Base):
    __tablename__ = "inference_logs"

    id = Column(BigInt, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    target_symbol = Column(String, index=True)
    predicted_price = Column(Float)
    actual_price = Column(Float, nullable=True)
    signal = Column(String) # BUY, SELL, HOLD
    confidence = Column(Float)
    processing_time = Column(Integer) # milliseconds

    trades = relationship("TradeExecution", back_populates="inference")
    snapshots = relationship("SectorSnapshot", back_populates="inference")

class TradeExecution(Base):
    __tablename__ = "trade_executions"

    alpaca_order_id = Column(String, primary_key=True, index=True)
    inference_id = Column(BigInt, ForeignKey("inference_logs.id"))
    status = Column(String) # FILLED, REJECTED, CANCELED
    quantity = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    realized_pnl = Column(Float, nullable=True)

    inference = relationship("InferenceLog", back_populates="trades")

class SectorSnapshot(Base):
    __tablename__ = "sector_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    inference_id = Column(BigInt, ForeignKey("inference_logs.id"))
    sector_avg_volatility = Column(Float)
    sector_trend_velocity = Column(Float)
    relative_strength = Column(Float)

    inference = relationship("InferenceLog", back_populates="snapshots")
