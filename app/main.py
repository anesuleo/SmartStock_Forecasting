#FastAPI app + /forecast/{item_id} endpoint
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .forecaster import generate_forecast
from .inventory_client import fetch_movements

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="SmartStock Forecasting Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/forecast/{item_id}")
def forecast(item_id: int, horizon: int = 30):
    """
    Returns a demand forecast for a given inventory item.
    
    - item_id: the inventory item to forecast
    - horizon: number of days to forecast into the future (default 30)
    """
    # 1. Pull historical OUT movements from the inventory service
    movements = fetch_movements(item_id)

    if not movements:
        raise HTTPException(
            status_code=404,
            detail=f"No sales history found for item {item_id}"
        )

    if len(movements) < 2:
        raise HTTPException(
            status_code=422,
            detail="Not enough historical data to generate a forecast (need at least 2 data points)"
        )

    # 2. Run Prophet forecast
    result = generate_forecast(movements, horizon=horizon)

    return {
        "item_id": item_id,
        "horizon_days": horizon,
        "forecast": result
    }