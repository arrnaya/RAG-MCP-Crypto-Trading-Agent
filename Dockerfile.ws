FROM python:3.12.4-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8765 8001
CMD ["python", "websocket_server.py"]