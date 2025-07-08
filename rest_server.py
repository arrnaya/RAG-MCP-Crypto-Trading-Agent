from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
from rag_pipeline import query
from loguru import logger
import os
import uuid
from prometheus_client import Counter, Histogram
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Metrics
api_requests = Counter("api_requests_total", "Total number of API requests")
api_latency = Histogram("api_latency_seconds", "API request latency")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
API_KEY = os.getenv("REST_API_KEY", "changeme")

class QueryRequest(BaseModel):
    question: str

@app.middleware("http")
async def authenticate(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    if request.url.path == "/health":
        return await call_next(request)
    token = request.headers.get("X-API-KEY")
    if token != API_KEY:
        logger.warning(f"Unauthorized API request [CID: {correlation_id}]")
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query")
async def ask(req: QueryRequest):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    api_requests.inc()
    with api_latency.time():
        logger.info(f"REST query: {req.question} [CID: {correlation_id}]")
        response = query(req.question)
    return JSONResponse(content={"response": response})