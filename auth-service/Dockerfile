FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY proto ./proto
COPY src ./src

EXPOSE 5001

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.app"]