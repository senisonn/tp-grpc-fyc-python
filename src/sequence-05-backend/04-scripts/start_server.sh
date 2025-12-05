#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Starting gRPC Server..."

if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}⚠️  No virtual environment found${NC}"
    fi
fi

if [ ! -f "generated/user_pb2.py" ]; then
    echo "📦 Generating proto stubs..."
    ./scripts/generate_proto.sh || { echo "Failed to generate stubs"; exit 1; }
fi

if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo -e "${GREEN}✅ Starting server on port ${SERVER_PORT:-50051}...${NC}"
python3 server.py
