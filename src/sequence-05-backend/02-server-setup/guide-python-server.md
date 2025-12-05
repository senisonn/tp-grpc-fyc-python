# Guide Complet : Mise en Place d'un Serveur Python gRPC

## Table des Matières

1. [Configuration de l'Environnement](#1-configuration-de-lenvironnement)
2. [Structure du Projet](#2-structure-du-projet)
3. [Installation des Dépendances](#3-installation-des-dépendances)
4. [Génération des Stubs Python](#4-génération-des-stubs-python)
5. [Implémentation du Premier Service](#5-implémentation-du-premier-service)
6. [Lancement du Serveur](#6-lancement-du-serveur)
7. [Test du Serveur](#7-test-du-serveur)
8. [Configuration Avancée](#8-configuration-avancée)

---

## 1. Configuration de l'Environnement

### 1.1 Prérequis

Avant de commencer, assurez-vous d'avoir :

- **Python 3.8+** installé
- **pip** (gestionnaire de paquets Python)
- **virtualenv** (recommandé pour isoler les dépendances)
- **protoc** (Protocol Buffer Compiler)
- Un **éditeur de code** (VS Code, PyCharm, etc.)

### 1.2 Vérification des Installations

```bash
# Vérifier Python
python3 --version
# Output attendu: Python 3.8.x ou supérieur

# Vérifier pip
pip3 --version

# Vérifier protoc
protoc --version
# Output attendu: libprotoc 3.x.x ou supérieur
```

### 1.3 Installation de protoc

**macOS (Homebrew) :**
```bash
brew install protobuf
```

**Ubuntu/Debian :**
```bash
sudo apt-get update
sudo apt-get install -y protobuf-compiler
```

**Windows :**
1. Télécharger depuis https://github.com/protocolbuffers/protobuf/releases
2. Extraire et ajouter au PATH

### 1.4 Créer un Environnement Virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Votre prompt devrait maintenant afficher (venv)
```

---

## 2. Structure du Projet

### 2.1 Créer la Structure

```bash
# Créer le projet
mkdir grpc-backend
cd grpc-backend

# Créer la structure de dossiers
mkdir -p proto
mkdir -p generated
mkdir -p services
mkdir -p models
mkdir -p interceptors
mkdir -p utils
mkdir -p tests
mkdir -p config
mkdir -p scripts

# Créer les fichiers __init__.py
touch generated/__init__.py
touch services/__init__.py
touch models/__init__.py
touch interceptors/__init__.py
touch utils/__init__.py
touch tests/__init__.py
touch config/__init__.py
```

### 2.2 Structure Finale

```
grpc-backend/
├── proto/
│   └── user.proto              # Définitions Protocol Buffer
├── generated/                   # Stubs Python générés
│   ├── __init__.py
│   ├── user_pb2.py
│   └── user_pb2_grpc.py
├── services/                    # Implémentation des services
│   ├── __init__.py
│   ├── user_service.py
│   └── base_service.py
├── models/                      # Modèles de données
│   ├── __init__.py
│   └── user.py
├── interceptors/                # Intercepteurs gRPC
│   ├── __init__.py
│   ├── logging_interceptor.py
│   └── auth_interceptor.py
├── utils/                       # Utilitaires
│   ├── __init__.py
│   ├── validators.py
│   └── errors.py
├── tests/                       # Tests
│   ├── __init__.py
│   └── test_user_service.py
├── config/                      # Configuration
│   ├── __init__.py
│   └── settings.py
├── scripts/                     # Scripts utilitaires
│   ├── generate_proto.sh
│   └── start_server.sh
├── requirements.txt             # Dépendances Python
├── server.py                    # Point d'entrée du serveur
├── .env                         # Variables d'environnement
├── .gitignore
└── README.md
```

---

## 3. Installation des Dépendances

### 3.1 Créer requirements.txt

Créez le fichier `requirements.txt` avec le contenu suivant :

```txt
# Core gRPC
grpcio==1.59.3
grpcio-tools==1.59.3
grpcio-reflection==1.59.3
protobuf==4.25.1

# Database drivers
psycopg2-binary==2.9.9    # PostgreSQL
pymongo==4.6.0            # MongoDB
redis==5.0.1              # Redis

# Validation
pydantic==2.5.2

# Environment variables
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-grpc==0.8.0
pytest-cov==4.1.0

# Utilities
python-dateutil==2.8.2
```

### 3.2 Installer les Dépendances

```bash
# Activer l'environnement virtuel si pas déjà fait
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list | grep grpc
```

---

## 4. Génération des Stubs Python

### 4.1 Créer le Fichier .proto

Créez `proto/user.proto` :

```protobuf
syntax = "proto3";

package user;

// Service de gestion des utilisateurs
service UserService {
  // Créer un utilisateur
  rpc CreateUser(CreateUserRequest) returns (User) {}
  
  // Obtenir un utilisateur par ID
  rpc GetUser(GetUserRequest) returns (User) {}
  
  // Lister les utilisateurs
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {}
  
  // Mettre à jour un utilisateur
  rpc UpdateUser(UpdateUserRequest) returns (User) {}
  
  // Supprimer un utilisateur
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse) {}
}

// Messages

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
  int64 updated_at = 5;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
  string password = 3;
}

message GetUserRequest {
  string user_id = 1;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total_count = 2;
}

message UpdateUserRequest {
  string user_id = 1;
  string name = 2;
  string email = 3;
}

message DeleteUserRequest {
  string user_id = 1;
}

message DeleteUserResponse {
  bool success = 1;
  string message = 2;
}
```

### 4.2 Script de Génération

Créez `scripts/generate_proto.sh` :

```bash
#!/bin/bash

# Script pour générer les stubs Python depuis les fichiers .proto

set -e

# Couleurs pour output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔨 Génération des stubs Python..."

# Vérifier que protoc est installé
if ! command -v python3 -m grpc_tools.protoc &> /dev/null; then
    echo -e "${RED}❌ grpcio-tools n'est pas installé${NC}"
    echo "Installez-le avec: pip install grpcio-tools"
    exit 1
fi

# Répertoires
PROTO_DIR="proto"
OUT_DIR="generated"

# Créer le répertoire de sortie s'il n'existe pas
mkdir -p "$OUT_DIR"

# Générer les stubs pour tous les fichiers .proto
for proto_file in "$PROTO_DIR"/*.proto; do
    if [ -f "$proto_file" ]; then
        echo "📄 Génération depuis: $proto_file"
        
        python3 -m grpc_tools.protoc \
            -I"$PROTO_DIR" \
            --python_out="$OUT_DIR" \
            --grpc_python_out="$OUT_DIR" \
            "$proto_file"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} $(basename "$proto_file") généré"
        else
            echo -e "${RED}✗${NC} Erreur lors de la génération de $(basename "$proto_file")"
            exit 1
        fi
    fi
done

# Créer __init__.py si nécessaire
if [ ! -f "$OUT_DIR/__init__.py" ]; then
    touch "$OUT_DIR/__init__.py"
fi

echo -e "${GREEN}✅ Génération terminée avec succès!${NC}"
echo ""
echo "Fichiers générés dans: $OUT_DIR/"
ls -lh "$OUT_DIR"
```

### 4.3 Rendre le Script Exécutable et Lancer

```bash
# Rendre exécutable
chmod +x scripts/generate_proto.sh

# Exécuter
./scripts/generate_proto.sh
```

**Fichiers générés :**
- `generated/user_pb2.py` - Messages (classes Python)
- `generated/user_pb2_grpc.py` - Service stubs et servicers

---

## 5. Implémentation du Premier Service

### 5.1 Modèle de Données

Créez `models/user.py` :

```python
"""
User data model
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class User:
    """User model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    
    def to_proto(self):
        """Convert to protobuf User message"""
        from generated import user_pb2
        return user_pb2.User(
            id=self.id,
            name=self.name,
            email=self.email,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @classmethod
    def from_proto(cls, proto_user):
        """Create User from protobuf message"""
        return cls(
            id=proto_user.id,
            name=proto_user.name,
            email=proto_user.email,
            created_at=proto_user.created_at,
            updated_at=proto_user.updated_at
        )
```

### 5.2 Utilitaires de Validation

Créez `utils/validators.py` :

```python
"""
Validation utilities
"""
import re
from typing import Optional


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate name
    Returns: (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"
    
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name must not exceed 100 characters"
    
    return True, None
```

### 5.3 Service Base

Créez `services/base_service.py` :

```python
"""
Base service class with common functionality
"""
import logging
from typing import Any


class BaseService:
    """Base class for all gRPC services"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_request(self, method_name: str, request: Any):
        """Log incoming request"""
        self.logger.info(f"Received {method_name} request")
        self.logger.debug(f"Request data: {request}")
    
    def log_response(self, method_name: str, response: Any):
        """Log outgoing response"""
        self.logger.info(f"Sending {method_name} response")
        self.logger.debug(f"Response data: {response}")
    
    def log_error(self, method_name: str, error: Exception):
        """Log error"""
        self.logger.error(f"Error in {method_name}: {str(error)}", exc_info=True)
```

### 5.4 Implémentation du Service UserService

Créez `services/user_service.py` :

```python
"""
UserService implementation
"""
import grpc
import hashlib
from datetime import datetime
from typing import Dict

from generated import user_pb2, user_pb2_grpc
from models.user import User
from services.base_service import BaseService
from utils.validators import validate_email, validate_password, validate_name


class UserService(user_pb2_grpc.UserServiceServicer, BaseService):
    """Implementation of UserService"""
    
    def __init__(self):
        super().__init__()
        # In-memory storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.logger.info("UserService initialized")
    
    def CreateUser(self, request, context):
        """Create a new user"""
        self.log_request("CreateUser", request)
        
        try:
            # Validate name
            is_valid, error_msg = validate_name(request.name)
            if not is_valid:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, error_msg)
            
            # Validate email
            is_valid, error_msg = validate_email(request.email)
            if not is_valid:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, error_msg)
            
            # Check if email already exists
            for user in self.users.values():
                if user.email == request.email:
                    context.abort(
                        grpc.StatusCode.ALREADY_EXISTS,
                        f"User with email {request.email} already exists"
                    )
            
            # Validate password
            is_valid, error_msg = validate_password(request.password)
            if not is_valid:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, error_msg)
            
            # Create user
            user = User(
                name=request.name,
                email=request.email,
                password_hash=self._hash_password(request.password)
            )
            
            self.users[user.id] = user
            
            self.logger.info(f"User created: {user.id}")
            response = user.to_proto()
            self.log_response("CreateUser", response)
            
            return response
            
        except grpc.RpcError:
            raise
        except Exception as e:
            self.log_error("CreateUser", e)
            context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    def GetUser(self, request, context):
        """Get user by ID"""
        self.log_request("GetUser", request)
        
        try:
            # Validate user_id
            if not request.user_id:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "user_id is required"
                )
            
            # Get user
            user = self.users.get(request.user_id)
            if not user:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"User {request.user_id} not found"
                )
            
            response = user.to_proto()
            self.log_response("GetUser", response)
            
            return response
            
        except grpc.RpcError:
            raise
        except Exception as e:
            self.log_error("GetUser", e)
            context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    def ListUsers(self, request, context):
        """List users with pagination"""
        self.log_request("ListUsers", request)
        
        try:
            # Validate pagination parameters
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            page_size = min(page_size, 100)  # Max 100 items per page
            
            # Get all users
            all_users = list(self.users.values())
            total_count = len(all_users)
            
            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            # Get page of users
            page_users = all_users[start_idx:end_idx]
            
            # Convert to proto
            response = user_pb2.ListUsersResponse(
                users=[user.to_proto() for user in page_users],
                total_count=total_count
            )
            
            self.log_response("ListUsers", response)
            return response
            
        except grpc.RpcError:
            raise
        except Exception as e:
            self.log_error("ListUsers", e)
            context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    def UpdateUser(self, request, context):
        """Update user"""
        self.log_request("UpdateUser", request)
        
        try:
            # Validate user_id
            if not request.user_id:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "user_id is required"
                )
            
            # Get user
            user = self.users.get(request.user_id)
            if not user:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"User {request.user_id} not found"
                )
            
            # Validate and update name
            if request.name:
                is_valid, error_msg = validate_name(request.name)
                if not is_valid:
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, error_msg)
                user.name = request.name
            
            # Validate and update email
            if request.email:
                is_valid, error_msg = validate_email(request.email)
                if not is_valid:
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, error_msg)
                
                # Check if email already exists for another user
                for uid, u in self.users.items():
                    if u.email == request.email and uid != request.user_id:
                        context.abort(
                            grpc.StatusCode.ALREADY_EXISTS,
                            f"Email {request.email} already in use"
                        )
                
                user.email = request.email
            
            # Update timestamp
            user.updated_at = int(datetime.now().timestamp())
            
            self.logger.info(f"User updated: {user.id}")
            response = user.to_proto()
            self.log_response("UpdateUser", response)
            
            return response
            
        except grpc.RpcError:
            raise
        except Exception as e:
            self.log_error("UpdateUser", e)
            context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    def DeleteUser(self, request, context):
        """Delete user"""
        self.log_request("DeleteUser", request)
        
        try:
            # Validate user_id
            if not request.user_id:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "user_id is required"
                )
            
            # Check if user exists
            if request.user_id not in self.users:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"User {request.user_id} not found"
                )
            
            # Delete user
            del self.users[request.user_id]
            
            self.logger.info(f"User deleted: {request.user_id}")
            response = user_pb2.DeleteUserResponse(
                success=True,
                message=f"User {request.user_id} deleted successfully"
            )
            self.log_response("DeleteUser", response)
            
            return response
            
        except grpc.RpcError:
            raise
        except Exception as e:
            self.log_error("DeleteUser", e)
            context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
```

---

## 6. Lancement du Serveur

### 6.1 Fichier de Configuration

Créez `config/settings.py` :

```python
"""
Server configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Server settings"""
    
    # Server
    HOST = os.getenv('SERVER_HOST', '[::]')
    PORT = os.getenv('SERVER_PORT', '50051')
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '10'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Database (for future use)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'grpc_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    @classmethod
    def get_server_address(cls):
        """Get full server address"""
        return f"{cls.HOST}:{cls.PORT}"


settings = Settings()
```

### 6.2 Fichier .env

Créez `.env` :

```env
# Server Configuration
SERVER_HOST=[::]
SERVER_PORT=50051
MAX_WORKERS=10

# Logging
LOG_LEVEL=INFO

# Database (for future use)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=grpc_db
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 6.3 Serveur Principal

Créez `server.py` :

```python
"""
gRPC Server main entry point
"""
import grpc
from concurrent import futures
import logging
import signal
import sys

from generated import user_pb2_grpc
from services.user_service import UserService
from config.settings import settings


def configure_logging():
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('server.log')
        ]
    )


def serve():
    """Start gRPC server"""
    # Configure logging
    configure_logging()
    logger = logging.getLogger(__name__)
    
    # Create server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)
    )
    
    # Add services
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(),
        server
    )
    
    # Add reflection (for tools like grpcurl)
    from grpc_reflection.v1alpha import reflection
    SERVICE_NAMES = (
        user_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Start server
    server_address = settings.get_server_address()
    server.add_insecure_port(server_address)
    server.start()
    
    logger.info(f"🚀 Server started on {server_address}")
    logger.info(f"⚙️  Max workers: {settings.MAX_WORKERS}")
    logger.info(f"📝 Log level: {settings.LOG_LEVEL}")
    logger.info("Press Ctrl+C to stop")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down server...")
        server.stop(grace=5)
        logger.info("Server stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for termination
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
```

### 6.4 Script de Démarrage

Créez `scripts/start_server.sh` :

```bash
#!/bin/bash

# Script pour démarrer le serveur gRPC

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo "🚀 Démarrage du serveur gRPC..."

# Vérifier que l'environnement virtuel est activé
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Générer les stubs si nécessaire
if [ ! -f "generated/user_pb2.py" ]; then
    echo "📦 Génération des stubs Proto..."
    ./scripts/generate_proto.sh
fi

echo -e "${GREEN}✅ Lancement du serveur...${NC}"
python3 server.py
```

Rendre exécutable :

```bash
chmod +x scripts/start_server.sh
```

### 6.5 Lancer le Serveur

```bash
# Méthode 1 : Directement
python3 server.py

# Méthode 2 : Avec le script
./scripts/start_server.sh
```

**Output attendu :**
```
2024-01-15 10:30:00 - __main__ - INFO - 🚀 Server started on [::]:50051
2024-01-15 10:30:00 - __main__ - INFO - ⚙️  Max workers: 10
2024-01-15 10:30:00 - __main__ - INFO - 📝 Log level: INFO
2024-01-15 10:30:00 - __main__ - INFO - Press Ctrl+C to stop
```

---

## 7. Test du Serveur

### 7.1 Avec grpcurl

```bash
# Liste les services
grpcurl -plaintext localhost:50051 list

# Décrit le service
grpcurl -plaintext localhost:50051 describe user.UserService

# Créer un utilisateur
grpcurl -plaintext -d '{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}' localhost:50051 user.UserService/CreateUser

# Obtenir un utilisateur (remplacer USER_ID)
grpcurl -plaintext -d '{
  "user_id": "USER_ID_HERE"
}' localhost:50051 user.UserService/GetUser

# Lister les utilisateurs
grpcurl -plaintext -d '{
  "page": 1,
  "page_size": 10
}' localhost:50051 user.UserService/ListUsers
```

### 7.2 Client Python de Test

Créez `test_client.py` :

```python
"""
Simple test client for UserService
"""
import grpc
from generated import user_pb2, user_pb2_grpc


def run():
    # Create channel
    with grpc.insecure_channel('localhost:50051') as channel:
        # Create stub
        stub = user_pb2_grpc.UserServiceStub(channel)
        
        print("=== Testing UserService ===\n")
        
        # 1. Create user
        print("1. Creating user...")
        try:
            create_request = user_pb2.CreateUserRequest(
                name="Alice Smith",
                email="alice@example.com",
                password="SecurePass123"
            )
            user = stub.CreateUser(create_request)
            print(f"✅ User created: {user.id}")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}\n")
            user_id = user.id
        except grpc.RpcError as e:
            print(f"❌ Error: {e.details()}\n")
            return
        
        # 2. Get user
        print("2. Getting user...")
        try:
            get_request = user_pb2.GetUserRequest(user_id=user_id)
            user = stub.GetUser(get_request)
            print(f"✅ User retrieved: {user.name}\n")
        except grpc.RpcError as e:
            print(f"❌ Error: {e.details()}\n")
        
        # 3. Update user
        print("3. Updating user...")
        try:
            update_request = user_pb2.UpdateUserRequest(
                user_id=user_id,
                name="Alice Johnson",
                email="alice.johnson@example.com"
            )
            user = stub.UpdateUser(update_request)
            print(f"✅ User updated: {user.name}\n")
        except grpc.RpcError as e:
            print(f"❌ Error: {e.details()}\n")
        
        # 4. List users
        print("4. Listing users...")
        try:
            list_request = user_pb2.ListUsersRequest(page=1, page_size=10)
            response = stub.ListUsers(list_request)
            print(f"✅ Found {response.total_count} user(s)")
            for user in response.users:
                print(f"   - {user.name} ({user.email})")
            print()
        except grpc.RpcError as e:
            print(f"❌ Error: {e.details()}\n")
        
        # 5. Delete user
        print("5. Deleting user...")
        try:
            delete_request = user_pb2.DeleteUserRequest(user_id=user_id)
            response = stub.DeleteUser(delete_request)
            print(f"✅ {response.message}\n")
        except grpc.RpcError as e:
            print(f"❌ Error: {e.details()}\n")
        
        print("=== Tests completed ===")


if __name__ == '__main__':
    run()
```

Exécuter le client :

```bash
python3 test_client.py
```

---

## 8. Configuration Avancée

### 8.1 Logging Interceptor

Créez `interceptors/logging_interceptor.py` :

```python
"""
Logging interceptor for gRPC
"""
import logging
import grpc
from typing import Callable, Any


class LoggingInterceptor(grpc.ServerInterceptor):
    """Interceptor to log all incoming requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails
    ) -> grpc.RpcMethodHandler:
        """Intercept and log requests"""
        
        # Log the request
        self.logger.info(f"📥 Request: {handler_call_details.method}")
        
        # Continue with the request
        return continuation(handler_call_details)
```

### 8.2 Utiliser l'Interceptor

Modifiez `server.py` pour ajouter l'interceptor :

```python
from interceptors.logging_interceptor import LoggingInterceptor

def serve():
    # ... existing code ...
    
    # Create server with interceptors
    interceptors = [LoggingInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS),
        interceptors=interceptors
    )
    
    # ... rest of the code ...
```

### 8.3 Docker Support

Créez `Dockerfile` :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Generate proto stubs
RUN python -m grpc_tools.protoc \
    -I proto \
    --python_out=generated \
    --grpc_python_out=generated \
    proto/*.proto

EXPOSE 50051

CMD ["python", "server.py"]
```

Créez `docker-compose.yml` :

```yaml
version: '3.8'

services:
  grpc-server:
    build: .
    ports:
      - "50051:50051"
    environment:
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=50051
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
```

**Lancer avec Docker :**

```bash
# Build
docker-compose build

# Run
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 8.4 .gitignore

Créez `.gitignore` :

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Generated files
generated/*.py
!generated/__init__.py

# Logs
*.log
logs/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 📊 Résumé

Vous avez maintenant un serveur gRPC Python complet avec :

✅ Structure de projet professionnelle
✅ Service CRUD complet (UserService)
✅ Validation des entrées
✅ Gestion des erreurs robuste
✅ Logging structuré
✅ Intercepteurs
✅ Support Docker
✅ Scripts utilitaires
✅ Client de test

## 🎯 Prochaines Étapes

1. Ajouter une vraie base de données (PostgreSQL)
2. Implémenter l'authentification JWT
3. Ajouter des tests unitaires
4. Configurer TLS/SSL
5. Ajouter du monitoring (Prometheus)
6. Implémenter le streaming

---

**Bon développement ! 🚀**
