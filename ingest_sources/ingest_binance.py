import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

BINANCE_API = "https://api.binance.com/api/v3/klines"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_technical_data(symbol, interval="5m"):
    try:
        symbol = f"{symbol}USDT"
        params = {"symbol": symbol, "interval": interval, "limit": 100}
        response = requests.get(BINANCE_API, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Error fetching Binance data for {symbol}: {e}")
        raise