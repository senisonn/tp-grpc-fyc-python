#!/bin/bash

# Script de génération des stubs JavaScript pour gRPC-Web
# Nécessite: protoc, protoc-gen-grpc-web

set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔨 Generating JavaScript stubs for gRPC-Web..."

# Vérifier les prérequis
command -v protoc >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc not found. Please install Protocol Buffers compiler.${NC}" 
    exit 1
}

command -v protoc-gen-grpc-web >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc-gen-grpc-web not found.${NC}"
    echo "Install it from: https://github.com/grpc/grpc-web/releases"
    exit 1
}

# Dossiers
PROTO_DIR="${PROTO_DIR:-./proto}"
OUT_DIR="${OUT_DIR:-./src/proto}"

# Créer le dossier de sortie
mkdir -p "$OUT_DIR"

echo "📂 Proto directory: $PROTO_DIR"
echo "📂 Output directory: $OUT_DIR"

# Générer pour chaque fichier .proto
for proto_file in "$PROTO_DIR"/*.proto; do
    if [ -f "$proto_file" ]; then
        echo "Processing: $(basename "$proto_file")"
        
        protoc \
            --js_out=import_style=commonjs:"$OUT_DIR" \
            --grpc-web_out=import_style=commonjs,mode=grpcwebtext:"$OUT_DIR" \
            -I="$PROTO_DIR" \
            "$proto_file"
    fi
done

echo -e "${GREEN}✓ JavaScript stubs generated successfully!${NC}"
echo "Files created in: $OUT_DIR"
