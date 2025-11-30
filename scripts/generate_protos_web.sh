set -e

echo "🌐 Génération des stubs gRPC-Web..."

PROTO_DIR="./proto"
OUT_DIR="./frontend/src/proto"

mkdir -p ${OUT_DIR}

# Génération JavaScript + gRPC-Web
protoc -I=${PROTO_DIR} \
  --js_out=import_style=commonjs:${OUT_DIR} \
  --grpc-web_out=import_style=commonjs,mode=grpcwebtext:${OUT_DIR} \
  ${PROTO_DIR}/auth.proto \
  ${PROTO_DIR}/chat.proto \
  ${PROTO_DIR}/common.proto

echo "✅ Stubs gRPC-Web générés!"