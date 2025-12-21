FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les sources et les proto du service chat
COPY proto ./proto
COPY src ./src

# Ajouter le proto au PYTHONPATH
ENV PYTHONPATH=/app/proto:$PYTHONPATH

EXPOSE 50051

# Lancer le serveur gRPC de chat
CMD ["python", "-m", "src.server"]
