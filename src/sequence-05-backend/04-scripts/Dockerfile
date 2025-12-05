FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Generate proto stubs
RUN python -m grpc_tools.protoc \
    -I proto \
    --python_out=generated \
    --grpc_python_out=generated \
    proto/*.proto

# Create non-root user
RUN useradd -m -u 1000 grpcuser && \
    chown -R grpcuser:grpcuser /app
USER grpcuser

EXPOSE 50051

CMD ["python", "server.py"]
