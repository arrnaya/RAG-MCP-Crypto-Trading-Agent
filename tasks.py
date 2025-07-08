import os
import uuid
import traceback
from celery import Celery
from loguru import logger
import requests
from ingest_sources.ingest_coinmarketcap import fetch_top_50_symbols
from ingest_sources.ingest_binance import fetch_technical_data
from ingest_sources.ingest_sentiment import fetch_sentiment
from haystack.document_stores import WeaviateDocumentStore
from prometheus_client import Counter, Histogram

# Metrics
ingestion_count = Counter("ingestion_tasks_total", "Total number of ingestion tasks")
ingestion_latency = Histogram("ingestion_latency_seconds", "Ingestion task latency")

SLACK_WEBHOOK = os.getenv("SLACK_ALERT_WEBHOOK", "https://hooks.slack.com/services/YOUR/PLACEHOLDER/WEBHOOK")
store = WeaviateDocumentStore(url="http://weaviate:8080")

app = Celery("tasks", broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"))
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]

def slack_alert(message):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=5)
        logger.info(f"Slack alert sent [CID: {correlation_id}]")
    except Exception as e:
        logger.error(f"Slack alert failed: {e} [CID: {correlation_id}]")

@app.task(bind=True, max_retries=3)
def ingest_all_data(self):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        ingestion_count.inc()
        with ingestion_latency.time():
            logger.info(f"Starting ingestion task [CID: {correlation_id}]")
            symbols = fetch_top_50_symbols()
            logger.info(f"Fetched {len(symbols)} top coins [CID: {correlation_id}]")
            for symbol in symbols:
                indicators = fetch_technical_data(symbol)
                sentiment = fetch_sentiment(symbol)
                doc = {
                    "content": f"{symbol} technicals and sentiment",
                    "meta": {
                        "symbol": symbol,
                        "indicators": indicators,
                        "sentiment": sentiment,
                    }
                }
                store.write_documents([doc], duplicate_documents="skip")
            logger.info(f"Ingestion task completed successfully [CID: {correlation_id}]")
    except Exception as e:
        error_msg = f"Ingestion failed: {str(e)} [CID: {correlation_id}]"
        logger.exception(error_msg)
        slack_alert(f"🚨 {error_msg}\n```{traceback.format_exc()}```")
        raise self.retry(exc=e, countdown=60)