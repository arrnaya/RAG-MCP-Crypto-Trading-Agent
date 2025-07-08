import asyncio
import websockets
import os
import uuid
from rag_pipeline import query
from loguru import logger
from prometheus_client import Counter, Gauge

# Metrics
ws_connections = Gauge("ws_connections_active", "Number of active WebSocket connections")
ws_messages = Counter("ws_messages_total", "Total number of WebSocket messages received")

WS_PORT = int(os.getenv("WS_PORT", 8765))
WS_API_KEY = os.getenv("WS_API_KEY", "changeme")

async def handler(websocket, path):
    correlation_id = str(uuid.uuid4())
    logger.configure(extra={"correlation_id": correlation_id})
    try:
        key = websocket.request_headers.get("X-API-KEY")
        if key != WS_API_KEY:
            await websocket.send("Unauthorized")
            logger.warning(f"Unauthorized WebSocket connection [CID: {correlation_id}]")
            return
        ws_connections.inc()
        await websocket.send("Connected. Ask your question.")
        async for message in websocket:
            ws_messages.inc()
            logger.info(f"WS received: {message} [CID: {correlation_id}]")
            response = query(message)
            await websocket.send(response)
    except Exception as e:
        logger.error(f"WebSocket error: {e} [CID: {correlation_id}]")
    finally:
        ws_connections.dec()

start_server = websockets.serve(handler, "0.0.0.0", WS_PORT, ssl=None)

if __name__ == "__main__":
    logger.info(f"Starting WebSocket server on port {WS_PORT}")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()