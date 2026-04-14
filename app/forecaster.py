#All Prophet logic lives here
import pandas as pd
from prophet import Prophet


def generate_forecast(movements: list[dict], horizon: int = 30) -> list[dict]:
    """
    Takes a list of sales movements and returns a Prophet forecast.

    movements: [{"movement_date": "2024-01-01", "quantity": 5}, ...]
    horizon:   number of days to predict into the future

    Returns a list of forecast rows:
    [{"ds": "2024-02-01", "yhat": 4.2, "yhat_lower": 2.1, "yhat_upper": 6.3}, ...]
    """

    # --- 1. Build a daily aggregated DataFrame ---
    df = pd.DataFrame(movements)
    df["ds"] = pd.to_datetime(df["movement_date"])
    df["y"] = df["quantity"]

    # Aggregate by day (multiple sales on same day get summed)
    df = df.groupby("ds", as_index=False)["y"].sum()

    # Fill in missing days with 0 (no sales = 0 demand that day)
    full_range = pd.date_range(df["ds"].min(), df["ds"].max(), freq="D")
    df = df.set_index("ds").reindex(full_range, fill_value=0).reset_index()
    df.columns = ["ds", "y"]

    # --- 2. Fit Prophet ---
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,   # daily rarely useful for inventory
        interval_width=0.80        # 80% confidence interval
    )
    model.fit(df)

    # --- 3. Generate future dataframe and predict ---
    future = model.make_future_dataframe(periods=horizon, freq="D")
    forecast = model.predict(future)

    # --- 4. Return only the future portion, cleaned up ---
    future_only = forecast[forecast["ds"] > df["ds"].max()].copy()

    result = future_only[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    result["ds"] = result["ds"].dt.strftime("%Y-%m-%d")

    # Clamp negatives (demand can't be negative)
    result["yhat"] = result["yhat"].clip(lower=0).round(2)
    result["yhat_lower"] = result["yhat_lower"].clip(lower=0).round(2)
    result["yhat_upper"] = result["yhat_upper"].clip(lower=0).round(2)

    return result.to_dict(orient="records")