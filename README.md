# 🧠 RAG Crypto Trading Agent

A production-ready Retrieval-Augmented Generation (RAG) agent for cryptocurrency trading, leveraging real-time market data, technical indicators, and sentiment analysis to provide expert trading insights.

## 🧩 Features

- **Real-Time Data Ingestion**: Fetches data from CoinMarketCap, Binance, and The Tie APIs for market listings, technical indicators, and sentiment analysis.
- **RAG Pipeline**: Combines BM25 and embedding-based retrieval with an LLM via OpenRouter.ai for context-aware trading advice.
- **Interfaces**:
  - REST API for programmatic access.
  - WebSocket for real-time interaction.
  - Streamlit UI for an interactive dashboard.
- **Conversation Memory**: Maintains context across user queries.
- **Scheduled Ingestion**: Uses Celery for periodic data updates.
- **Monitoring**: Prometheus metrics and Grafana dashboards for system performance.
- **Error Handling**: Structured logging, Sentry integration, and Slack alerts for failures.
- **Dockerized Deployment**: Fully containerized with Docker Compose for scalability and reliability.

## 🛠️ Prerequisites

- Docker and Docker Compose
- API keys for:
  - [CoinMarketCap](https://coinmarketcap.com/api/)
  - [The Tie](https://www.thetie.io/)
  - [OpenRouter](https://openrouter.ai/)
- Slack webhook for alerts (optional)
- Sentry DSN for error tracking (optional)

## 🚀 Quick Start

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-repo/rag-trading-agent.git
   cd rag-trading-agent
   ```
2. **Set Up Environment Variables**
   Copy `.env.example` to `.env` and fill in your API keys:

   ```bash
   cp .env.example .env
   nano .env
   ```
3. **Build and Run**

   ```bash
   docker-compose up --build
   ```
4. **Access the Services**

   - **Streamlit UI**: `http://localhost:8501`
   - **REST API**: `http://localhost:8000`
   - **WebSocket**: `ws://localhost:8765`
   - **Prometheus**: `http://localhost:9090`
   - **Grafana**: `http://localhost:3000` (login as anonymous)

## 📊 Usage

### Streamlit UI

- Open `http://localhost:8501` in your browser.
- Enter trading-related questions (e.g., "Should I buy BTC now?").
- View responses and conversation history.

### REST API

- Health check: `curl http://localhost:8000/health`
- Query endpoint:
  ```bash
  curl -X POST http://localhost:8000/query \
       -H "X-API-KEY: your_rest_api_key" \
       -H "Content-Type: application/json" \
       -d '{"question": "What is the current sentiment for ETH?"}'
  ```

### WebSocket

- Connect using a WebSocket client with the header `X-API-KEY: your_ws_api_key`.
- Example in Python:
  ```python
  import websockets
  async def connect():
      async with websockets.connect("ws://localhost:8765", extra_headers={"X-API-KEY": "your_ws_api_key"}) as ws:
          await ws.send("Should I buy BTC now?")
          response = await ws.recv()
          print(response)
  ```

### Monitoring

- View metrics at `http://localhost:9090`.
- Access Grafana dashboards at `http://localhost:3000` for real-time system insights.

## 🛠️ Configuration

- **Weaviate**: Configured in `weaviate_config.json`. Adjust vectorizer settings as needed.
- **Celery**: Configured for 4 workers. Modify `celery_worker.sh` for different concurrency levels.
- **Prometheus/Grafana**: Configured in `monitoring/`. Add custom metrics or dashboards as needed.

## 🐛 Troubleshooting

- **Service Failures**: Check container logs with `docker-compose logs <service>`.
- **API Errors**: Verify API keys in `.env` and ensure external APIs are accessible.
- **Weaviate Issues**: Ensure the `weaviate` service is healthy (`curl http://localhost:8080/v1/.well-known/ready`).
- **Sentry Alerts**: If configured, errors are reported to Sentry for detailed debugging.
- **Slack Alerts**: Ingestion failures are sent to the configured Slack webhook.

## 🔄 Scaling

- **Horizontal Scaling**: Increase `celery-worker` replicas in `docker-compose.yml`.
- **Weaviate**: Configure sharding and replication in `weaviate_config.json` for large datasets.
- **Load Balancing**: Add a reverse proxy (e.g., Nginx) for the REST API and WebSocket.

## 📝 Notes

- Replace placeholder API keys in `.env` with valid keys.
- The system skips stablecoins and ETFs during ingestion.
- For production, enable HTTPS by configuring SSL in `docker-compose.yml`.
- Regularly update dependencies in `requirements.txt`.

## 🤝 Contributing

Contributions are welcome! Please open an issue or PR on GitHub.

## 📜 License

MIT License
