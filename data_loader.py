import uuid
from haystack.document_stores import WeaviateDocumentStore
from haystack.utils import convert_files_to_docs
from haystack.nodes import PreProcessor
from loguru import logger
import sentry_sdk

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN", ""), traces_sample_rate=1.0)

store = WeaviateDocumentStore(
    url="http://weaviate:8080",
    timeout=(10, 60),
    batch_size=1000
)

preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    split_by="word",
    split_length=300,
    split_respect_sentence_boundary=True,
)

def ingest_local_docs(folder_path="./docs"):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        logger.info(f"Starting document ingestion [CID: {correlation_id}]")
        raw_docs = convert_files_to_docs(dir_path=folder_path)
        processed_docs = preprocessor.process(raw_docs)
        store.write_documents(processed_docs, duplicate_documents="skip")
        logger.info(f"Successfully ingested {len(processed_docs)} documents [CID: {correlation_id}]")
    except Exception as e:
        logger.exception(f"Failed to ingest documents [CID: {correlation_id}]")
        sentry_sdk.capture_exception(e)
        raise