FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les sources et les proto du service logging
COPY proto ./proto
COPY src ./src

# Ajouter le proto au PYTHONPATH
ENV PYTHONPATH=/app/proto:$PYTHONPATH

EXPOSE 50052

# Lancer le serveur gRPC de logging
CMD ["python", "-m", "src.server"]
