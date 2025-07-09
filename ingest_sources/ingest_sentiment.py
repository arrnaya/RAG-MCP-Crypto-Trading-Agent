# import requests
# import os
# from loguru import logger
# from tenacity import retry, stop_after_attempt, wait_exponential

# TIE_API_KEY = os.getenv("TIE_API_KEY")
# TIE_URL = "https://api.thetie.io/v1/sentiment"

# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
# def fetch_sentiment(symbol):
#     try:
#         headers = {"Authorization": f"Bearer {TIE_API_KEY}"}
#         response = requests.get(f"{TIE_URL}?symbol={symbol}", headers=headers, timeout=10)
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         logger.warning(f"Sentiment fetch failed for {symbol}: {e}")
#         raise

import requests
import os
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

SANTIMENT_API_KEY = os.getenv("SANTIMENT_API_KEY")
SANTIMENT_URL = "https://api.santiment.net/graphql"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_sentiment(slug):
    try:
        headers = {"Authorization": f"Apikey {SANTIMENT_API_KEY}"}
        query = """
        query {
          getMetric(metric: "sentiment_balance_total") {
            timeseriesData(
              slug: "%s"
              from: "utc_now-1d"
              to: "utc_now"
              interval: "1d"
            ) {
              datetime
              value
            }
          }
        }
        """ % slug
        response = requests.post(SANTIMENT_URL, headers=headers, json={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'errors' in data:
            logger.warning(f"Error fetching sentiment for {slug}: {data['errors']}")
            return {"sentiment_balance": None}
        timeseries = data.get('data', {}).get('getMetric', {}).get('timeseriesData', [])
        if timeseries:
            sentiment_score = timeseries[-1]['value']
            logger.info(f"Fetched sentiment for {slug}: {sentiment_score}")
            return {"sentiment_balance": sentiment_score}
        else:
            logger.warning(f"No sentiment data for {slug}")
            return {"sentiment_balance": None}
    except Exception as e:
        logger.warning(f"Sentiment fetch failed for {slug}: {e}")
        raise