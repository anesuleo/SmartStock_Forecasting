#Fetches OUT movements from your inventory API
import os
import requests

INVENTORY_API = os.getenv("INVENTORY_API_URL", "http://localhost:8002")


def fetch_movements(item_id: int) -> list[dict]:
    """
    Fetches all OUT (sale) movements for a given inventory item
    from the inventory microservice.

    Returns a list of dicts with 'movement_date' and 'quantity'.
    """
    try:
        response = requests.get(
        f"{INVENTORY_API}/api/movements",
        params={"item_id": item_id, "limit": 1000},
        timeout=30
    )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to reach inventory service: {e}")

    all_movements = response.json()

    # Just return all results directly — already filtered by the API
    sales = [
        {
            "movement_date": m["movement_date"],
            "quantity": m["quantity"]
        }
        for m in response.json()
        if m["movement_type"] == "OUT"
    ]

    return sales