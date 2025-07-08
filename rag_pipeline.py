import os
import uuid
from haystack.document_stores import WeaviateDocumentStore
from haystack.nodes import PromptNode, PromptTemplate, BM25Retriever, EmbeddingRetriever
from haystack.pipelines import Pipeline
from loguru import logger
import sentry_sdk
from prometheus_client import Counter, Histogram

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN", ""), traces_sample_rate=1.0)

# Metrics
query_count = Counter("rag_query_total", "Total number of queries processed")
query_latency = Histogram("rag_query_latency_seconds", "Query processing latency")

store = WeaviateDocumentStore(url="http://weaviate:8080")
retriever = BM25Retriever(document_store=store)
embedding_retriever = EmbeddingRetriever(
    document_store=store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    use_gpu=False
)

trader_prompt = PromptTemplate(
    name="crypto-trader-query",
    prompt="""
You are a professional cryptocurrency trader with a strong track record of profitable trades.
You rely on multi-timeframe technical analysis (MACD, RSI, Bollinger Bands, SMA, EMA) and crypto sentiment data.
Use the context below to craft an expert response to the user's question.

Context:
{{context}}

Question: {{query}}

Expert Trader's Answer:
""",
    input_variables=["query", "context"]
)

prompt_node = PromptNode(
    model_name_or_path="openrouter/llm",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_prompt_template=trader_prompt,
    api_base_url="https://openrouter.ai/api/v1",
    max_length=500
)

rag_pipeline = Pipeline()
rag_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
rag_pipeline.add_node(component=embedding_retriever, name="EmbeddingRetriever", inputs=["Retriever"])
rag_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["EmbeddingRetriever"])

def query(question):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        logger.info(f"Running query: {question} [CID: {correlation_id}]")
        query_count.inc()
        with query_latency.time():
            result = rag_pipeline.run(query=question, params={"Retriever": {"top_k": 10}})
        answer = result["answers"][0].answer
        logger.info(f"RAG response: {answer} [CID: {correlation_id}]")
        return answer
    except Exception as e:
        logger.exception(f"Error in RAG query pipeline [CID: {correlation_id}]")
        sentry_sdk.capture_exception(e)
        return "Sorry, I encountered an error while generating a response. Please try again."