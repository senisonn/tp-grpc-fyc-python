#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔨 Generating Python stubs from .proto files..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

if ! python3 -m grpc_tools.protoc --version &> /dev/null; then
    echo -e "${RED}❌ grpcio-tools not installed${NC}"
    echo "Install with: pip install grpcio-tools"
    exit 1
fi

PROTO_DIR="${PROTO_DIR:-proto}"
OUT_DIR="${OUT_DIR:-generated}"

if [ ! -d "$PROTO_DIR" ]; then
    echo -e "${RED}❌ Proto directory not found: $PROTO_DIR${NC}"
    exit 1
fi

mkdir -p "$OUT_DIR"

for proto_file in "$PROTO_DIR"/*.proto; do
    if [ -f "$proto_file" ]; then
        echo "📄 Generating: $(basename "$proto_file")"
        python3 -m grpc_tools.protoc \
            -I"$PROTO_DIR" \
            --python_out="$OUT_DIR" \
            --grpc_python_out="$OUT_DIR" \
            "$proto_file"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Generated successfully"
        else
            echo -e "${RED}✗${NC} Generation failed"
            exit 1
        fi
    fi
done

touch "$OUT_DIR/__init__.py"

echo -e "${GREEN}✅ All stubs generated successfully!${NC}"
ls -lh "$OUT_DIR"
