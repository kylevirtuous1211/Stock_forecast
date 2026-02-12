from fastapi import FastAPI
from backend.api.routes import router as api_router
from backend.db.database import engine, Base

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-time Sector Forecasting")

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Real-time Sector Forecasting API"}
