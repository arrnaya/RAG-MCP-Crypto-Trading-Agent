import uuid
import os
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from haystack.components.preprocessors import DocumentSplitter
from haystack import Document
from loguru import logger
import sentry_sdk

# Initialize Sentry for error tracking
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN", ""), traces_sample_rate=1.0)

# Initialize WeaviateDocumentStore
document_store = WeaviateDocumentStore(
    url="http://localhost:8080",
    timeout=(10, 60),
    batch_size=1000
)

# Initialize DocumentSplitter
preprocessor = DocumentSplitter(
    split_by="word",
    split_length=300,
    split_overlap=30
)


def ingest_local_docs(folder_path="./docs"):
    """
    Ingest documents from a local folder into WeaviateDocumentStore.

    Args:
        folder_path (str): Path to the folder containing .txt or .pdf files.
    """
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        logger.info(f"Starting document ingestion [CID: {correlation_id}]")

        # Read files and create documents
        documents = []
        for filename in os.listdir(folder_path):
            if filename.endswith((".txt", ".pdf")):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        documents.append(
                            Document(content=content, meta={"filename": filename}))
                except Exception as e:
                    logger.error(
                        f"Failed to read file {filename}: {e} [CID: {correlation_id}]")
                    continue

        if not documents:
            logger.warning(
                f"No valid documents found in {folder_path} [CID: {correlation_id}]")
            return

        # Preprocess documents
        processed_docs = preprocessor.run(documents=documents)
        logger.info(
            f"Preprocessed {len(processed_docs['documents'])} documents [CID: {correlation_id}]")

        # Write to Weaviate
        document_store.write_documents(
            processed_docs["documents"], policy="SKIP")
        logger.info(
            f"Successfully ingested {len(processed_docs['documents'])} documents [CID: {correlation_id}]")
    except Exception as e:
        logger.exception(f"Failed to ingest documents [CID: {correlation_id}]")
        sentry_sdk.capture_exception(e)
        raise
