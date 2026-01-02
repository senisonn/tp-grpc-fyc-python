@echo off
set PROTO_DIR=proto

echo.
echo [1/4] Logging Service...
python -m grpc_tools.protoc -I%PROTO_DIR% ^
    --python_out=logging-service/proto ^
    --grpc_python_out=logging-service/proto ^
    %PROTO_DIR%/logging.proto ^
    %PROTO_DIR%/common.proto

if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec generation Logging Service
    exit /b 1
)
echo [OK] Logging Service

echo.
echo [2/4] Chat Service...
python -m grpc_tools.protoc -I%PROTO_DIR% ^
    --python_out=chat-service/proto ^
    --grpc_python_out=chat-service/proto ^
    %PROTO_DIR%/chat.proto ^
    %PROTO_DIR%/logging.proto ^
    %PROTO_DIR%/common.proto

if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec generation Chat Service
    exit /b 1
)
echo [OK] Chat Service

echo.
echo [3/4] Auth Service...
python -m grpc_tools.protoc -I%PROTO_DIR% ^
    --python_out=auth-service/proto ^
    --grpc_python_out=auth-service/proto ^
    %PROTO_DIR%/auth.proto ^
    %PROTO_DIR%/logging.proto ^
    %PROTO_DIR%/common.proto

if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec generation Auth Service
    exit /b 1
)
echo [OK] Auth Service

echo.
echo [4/4] Gateway Service...
python -m grpc_tools.protoc -I%PROTO_DIR% ^
    --python_out=gateway-service/proto ^
    --grpc_python_out=gateway-service/proto ^
    %PROTO_DIR%/auth.proto ^
    %PROTO_DIR%/chat.proto ^
    %PROTO_DIR%/common.proto

if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec generation Gateway Service
    exit /b 1
)
echo [OK] Gateway Service

echo.
echo ========================================
echo   Generation terminee avec succes!
echo ========================================
echo.