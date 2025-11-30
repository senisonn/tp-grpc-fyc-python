set -e

echo "🔧 Génération des stubs Protocol Buffers..."

PROTO_DIR="./proto"

# Auth Service
echo "📦 Auth Service..."
python -m grpc_tools.protoc -I${PROTO_DIR} \
  --python_out=./auth-service/proto \
  --grpc_python_out=./auth-service/proto \
  ${PROTO_DIR}/auth.proto \
  ${PROTO_DIR}/common.proto

# Chat Service
echo "📦 Chat Service..."
python -m grpc_tools.protoc -I${PROTO_DIR} \
  --python_out=./chat-service/proto \
  --grpc_python_out=./chat-service/proto \
  ${PROTO_DIR}/chat.proto \
  ${PROTO_DIR}/logging.proto \
  ${PROTO_DIR}/common.proto

# Logging Service
echo "📦 Logging Service..."
python -m grpc_tools.protoc -I${PROTO_DIR} \
  --python_out=./logging-service/proto \
  --grpc_python_out=./logging-service/proto \
  ${PROTO_DIR}/logging.proto \
  ${PROTO_DIR}/common.proto

# Gateway Service
echo "📦 Gateway Service..."
python -m grpc_tools.protoc -I${PROTO_DIR} \
  --python_out=./gateway-service/proto \
  --grpc_python_out=./gateway-service/proto \
  ${PROTO_DIR}/auth.proto \
  ${PROTO_DIR}/chat.proto \
  ${PROTO_DIR}/common.proto

echo "✅ Génération terminée!"