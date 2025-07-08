#!/bin/bash
uvicorn rest_server:app --host 0.0.0.0 --port 8000 &
python websocket_server.py &
streamlit run streamlit_ui.py --server.port=8501 --server.address=0.0.0.0 &
python -m prometheus_client.start_http_server 8001