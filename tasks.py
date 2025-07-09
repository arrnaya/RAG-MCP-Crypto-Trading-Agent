import os
import uuid
import traceback
from celery import Celery
from loguru import logger
import requests
from ingest_sources.ingest_coingecko import fetch_top_50_symbols
from ingest_sources.ingest_binance import fetch_technical_data
from ingest_sources.ingest_sentiment import fetch_sentiment
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from haystack import Document
from prometheus_client import Counter, Histogram

# Metrics
ingestion_count = Counter("ingestion_tasks_total",
                          "Total number of ingestion tasks")
ingestion_latency = Histogram(
    "ingestion_latency_seconds", "Ingestion task latency")

store = WeaviateDocumentStore(url="http://localhost:8080")

app = Celery("tasks", broker=os.getenv(
    "CELERY_BROKER_URL", "redis://redis:6379/0"))
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]


@app.task(bind=True, max_retries=3)
def ingest_all_data(self):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        ingestion_count.inc()
        with ingestion_latency.time():
            logger.info(f"Starting ingestion task [CID: {correlation_id}]")
            coins = fetch_top_50_symbols()
            logger.info(
                f"Fetched {len(coins)} top coins [CID: {correlation_id}]")
            for coin in coins:
                symbol = coin["symbol"]
                slug = coin["slug"]
                indicators = fetch_technical_data(symbol)
                sentiment = fetch_sentiment(slug)
                doc = Document(
                    content=f"{symbol} technicals and sentiment",
                    meta={
                        "symbol": symbol,
                        "slug": slug,
                        "indicators": indicators,
                        "sentiment": sentiment,
                    }
                )
                store.write_documents([doc], policy="SKIP")
            logger.info(
                f"Ingestion task completed successfully [CID: {correlation_id}]")
    except Exception as e:
        error_msg = f"Ingestion failed: {str(e)} [CID: {correlation_id}]"
        logger.exception(error_msg)
        raise self.retry(exc=e, countdown=60)
