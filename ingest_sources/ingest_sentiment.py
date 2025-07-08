import requests
import os
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

TIE_API_KEY = os.getenv("TIE_API_KEY")
TIE_URL = "https://api.thetie.io/v1/sentiment"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_sentiment(symbol):
    try:
        headers = {"Authorization": f"Bearer {TIE_API_KEY}"}
        response = requests.get(f"{TIE_URL}?symbol={symbol}", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Sentiment fetch failed for {symbol}: {e}")
        raise