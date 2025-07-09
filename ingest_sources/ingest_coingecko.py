import requests
import os
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

COINGECKO_API_KEY = os.getenv("CG_API_KEY")
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_top_50_symbols():
    try:
        headers = {
            "x-cg-demo-api-key": COINGECKO_API_KEY} if COINGECKO_API_KEY else {}
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "sparkline": False
        }
        response = requests.get(
            COINGECKO_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Filter out stablecoins and ETFs
        stablecoins = ["usdt", "usdc", "dai", "busd", "tusd", "staked-ether", "wrapped-bitcoin", "wrapped-steth", "usds",
                       # Common stablecoin symbols
                       "wrapped-eeth", "weth", "binance-bridged-usdt-bnb-smart-chain", "ethena-usde", "ethena-staked-usde", "blackrock-usd-institutional-digital-liquidity-fund", "jito-staked-sol", "susds", "usd1-wlfi", "lombard-staked-btc", "binance-peg-weth"]
        return [
            {"symbol": coin["symbol"].upper(), "slug": coin["id"]}
            for coin in data
            if coin["symbol"].lower() not in stablecoins
            and "etf" not in coin.get("name", "").lower()
        ]
    except Exception as e:
        logger.exception(f"Failed to fetch CoinGecko top 50: {e}")
        raise
