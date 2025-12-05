#!/bin/bash

# Script de génération des stubs TypeScript pour gRPC-Web

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔨 Generating TypeScript stubs for gRPC-Web..."

# Vérifier les prérequis
command -v protoc >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc not found${NC}" 
    exit 1
}

command -v protoc-gen-grpc-web >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc-gen-grpc-web not found${NC}"
    exit 1
}

command -v protoc-gen-ts >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc-gen-ts not found${NC}"
    echo "Install with: npm install -g ts-protoc-gen"
    exit 1
}

PROTO_DIR="${PROTO_DIR:-./proto}"
OUT_DIR="${OUT_DIR:-./src/proto}"

mkdir -p "$OUT_DIR"

echo "📂 Proto directory: $PROTO_DIR"
echo "📂 Output directory: $OUT_DIR"

for proto_file in "$PROTO_DIR"/*.proto; do
    if [ -f "$proto_file" ]; then
        echo "Processing: $(basename "$proto_file")"
        
        # Generate TypeScript definitions
        protoc \
            --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
            --js_out=import_style=commonjs:"$OUT_DIR" \
            --ts_out=service=grpc-web:"$OUT_DIR" \
            --grpc-web_out=import_style=typescript,mode=grpcwebtext:"$OUT_DIR" \
            -I="$PROTO_DIR" \
            "$proto_file"
    fi
done

echo -e "${GREEN}✓ TypeScript stubs generated successfully!${NC}"
