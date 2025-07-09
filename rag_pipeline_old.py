import os
import uuid
from haystack_integrations.document_stores.weaviate.document_store import WeaviateDocumentStore
from haystack_integrations.components.retrievers.weaviate import WeaviateBM25Retriever
from haystack_integrations.components.retrievers.weaviate import WeaviateEmbeddingRetriever
# from weaviate_haystack import WeaviateDocumentStore, WeaviateBM25Retriever, WeaviateEmbeddingRetriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack import Pipeline
from loguru import logger
import sentry_sdk
from prometheus_client import Counter, Histogram

# Initialize Sentry for error tracking
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN", ""), traces_sample_rate=1.0)

# Metrics
query_count = Counter("rag_query_total", "Total number of queries processed")
query_latency = Histogram("rag_query_latency_seconds",
                          "Query processing latency")

# Initialize WeaviateDocumentStore
document_store = WeaviateDocumentStore(
    url="http://localhost:8080",
    timeout=(10, 60)
)

# Initialize retrievers
bm25_retriever = WeaviateBM25Retriever(document_store=document_store)
embedding_retriever = WeaviateEmbeddingRetriever(
    document_store=document_store,
    model="sentence-transformers/all-MiniLM-L6-v2"
)

trader_prompt = """
You are a professional cryptocurrency trader with a strong track record of profitable trades.
You rely on multi-timeframe technical analysis (MACD, RSI, Bollinger Bands, SMA, EMA) and crypto sentiment data.
Use the context below to craft an expert response to the user's question.

Context:
{{ context }}

Question: {{ question }}

Expert Trader's Answer:
"""

prompt_builder = PromptBuilder(template=trader_prompt)

prompt_node = OpenAIGenerator(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openrouter/llm",
    api_base_url="https://openrouter.ai/api/v1",
    generation_kwargs={"max_tokens": 500}
)

rag_pipeline = Pipeline()
rag_pipeline.add_component("bm25_retriever", bm25_retriever)
rag_pipeline.add_component("embedding_retriever", embedding_retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", prompt_node)

rag_pipeline.connect("bm25_retriever.documents",
                     "embedding_retriever.documents")
rag_pipeline.connect("embedding_retriever.documents",
                     "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "llm.prompt")


def query(question):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        logger.info(f"Running query: {question} [CID: {correlation_id}]")
        query_count.inc()
        with query_latency.time():
            result = rag_pipeline.run(
                data={
                    "bm25_retriever": {"query": question, "top_k": 10},
                    "embedding_retriever": {"query": question, "top_k": 10},
                    "prompt_builder": {"question": question}
                }
            )
        answer = result["llm"]["replies"][0]
        logger.info(f"RAG response: {answer} [CID: {correlation_id}]")
        return answer
    except Exception as e:
        logger.exception(
            f"Error in RAG query pipeline [CID: {correlation_id}]")
        sentry_sdk.capture_exception(e)
        return "Sorry, I encountered an error while generating a response. Please try again."
