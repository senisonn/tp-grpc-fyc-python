#!/bin/bash
PROTO_DIR="src/proto"
OUT_DIR="src/generated"
mkdir -p $OUT_DIR
protoc -I=$PROTO_DIR \
  --js_out=import_style=commonjs:$OUT_DIR \
  --grpc-web_out=import_style=commonjs,mode=grpcwebtext:$OUT_DIR \
  $PROTO_DIR/*.proto
echo "✅ Stubs generated"
