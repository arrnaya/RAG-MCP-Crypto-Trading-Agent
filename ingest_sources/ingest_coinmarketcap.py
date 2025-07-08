import requests
import os
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_top_50_symbols():
    try:
        headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
        params = {"start": "1", "limit": "50", "convert": "USD"}
        response = requests.get(CMC_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()["data"]
        return [coin["symbol"] for coin in data if "stable" not in coin.get("tags", []) and "ETF" not in coin.get("tags", [])]
    except Exception as e:
        logger.exception(f"Failed to fetch CMC top 50: {e}")
        raise