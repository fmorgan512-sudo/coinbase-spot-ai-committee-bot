import requests
from .coinbase_auth import build_jwt

BASE = "https://api.coinbase.com"


class CoinbaseClient:
    def __init__(self, timeout=20):
        self.timeout = timeout

    def _get(self, path: str, params=None):
        jwt_token = build_jwt("GET", path)
        r = requests.get(
            BASE + path,
            params=params,
            headers={"Authorization": f"Bearer {jwt_token}"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, json_body: dict):
        jwt_token = build_jwt("POST", path)
        r = requests.post(
            BASE + path,
            json=json_body,
            headers={"Authorization": f"Bearer {jwt_token}"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    # --- Key endpoints (Advanced Trade v3)
    def list_fills(self, product_id: str | None = None, limit: int = 100):
        params = {"limit": limit}
        if product_id:
            params["product_id"] = product_id
        return self._get("/api/v3/brokerage/orders/historical/fills", params=params)

    def list_orders(self, product_id: str | None = None, limit: int = 100):
        params = {"limit": limit}
        if product_id:
            params["product_id"] = product_id
        return self._get("/api/v3/brokerage/orders/historical/batch", params=params)

    def get_accounts(self):
        return self._get("/api/v3/brokerage/accounts")

    def create_order(self, order: dict):
        return self._post("/api/v3/brokerage/orders", order)
