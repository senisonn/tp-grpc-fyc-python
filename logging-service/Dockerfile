FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto ./proto
COPY src ./src

RUN mkdir -p /app/logs

EXPOSE 50053

CMD ["python", "-m", "src.server"]