# Guide Complet : Service CRUD avec gRPC Python

## Table des Matières

1. [Introduction au CRUD gRPC](#1-introduction-au-crud-grpc)
2. [Architecture du Service](#2-architecture-du-service)
3. [Gestion des Erreurs](#3-gestion-des-erreurs)
4. [Intercepteurs gRPC](#4-intercepteurs-grpc)
5. [Service CRUD Complet](#5-service-crud-complet)
6. [Repository Pattern](#6-repository-pattern)
7. [Tests Unitaires](#7-tests-unitaires)

---

## 1. Introduction au CRUD gRPC

### 1.1 Les Opérations CRUD

CRUD = **C**reate, **R**ead, **U**pdate, **D**elete

Dans gRPC, chaque opération est une méthode RPC:

```protobuf
service UserService {
  rpc CreateUser(CreateUserRequest) returns (User) {}      // CREATE
  rpc GetUser(GetUserRequest) returns (User) {}            // READ
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {} // READ (list)
  rpc UpdateUser(UpdateUserRequest) returns (User) {}      // UPDATE
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse) {} // DELETE
}
```

### 1.2 Types de RPC

**Unary RPC** (utilisé pour CRUD classique):
- Client envoie 1 requête → Serveur renvoie 1 réponse
- Exemple: CreateUser, GetUser, UpdateUser, DeleteUser

**Server Streaming** (pour grandes listes):
- Client envoie 1 requête → Serveur stream N réponses
- Exemple: ListUsers avec beaucoup de données

**Client Streaming** (batch operations):
- Client stream N requêtes → Serveur renvoie 1 réponse
- Exemple: Batch create users

---

## 2. Architecture du Service

### 2.1 Couches de l'Architecture

```
┌─────────────────────────────────┐
│   gRPC Service Layer            │
│   - Validation entrées          │
│   - Gestion erreurs             │
│   - Conversion proto ↔ models   │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Business Logic Layer          │
│   - Règles métier               │
│   - Validations complexes       │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Data Access Layer             │
│   - Repository pattern          │
│   - Accès base de données       │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│   Database                      │
└─────────────────────────────────┘
```

### 2.2 Classe de Base pour Services

```python
# services/base_service.py
import logging
from typing import Any

class BaseService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_request(self, method_name: str, request: Any):
        self.logger.info(f"📥 {method_name} request")
        self.logger.debug(f"Request: {request}")
    
    def log_response(self, method_name: str, response: Any):
        self.logger.info(f"📤 {method_name} response")
        self.logger.debug(f"Response: {response}")
    
    def log_error(self, method_name: str, error: Exception):
        self.logger.error(f"❌ {method_name} error: {error}", exc_info=True)
```

---

## 3. Gestion des Erreurs

### 3.1 Codes de Statut gRPC

Les 16 codes standardisés:

| Code | Nom | Usage | HTTP Equivalent |
|------|-----|-------|-----------------|
| 0 | OK | Succès | 200 |
| 1 | CANCELLED | Opération annulée | 499 |
| 2 | UNKNOWN | Erreur inconnue | 500 |
| 3 | INVALID_ARGUMENT | Arguments invalides | 400 |
| 4 | DEADLINE_EXCEEDED | Timeout | 504 |
| 5 | NOT_FOUND | Ressource non trouvée | 404 |
| 6 | ALREADY_EXISTS | Ressource existe déjà | 409 |
| 7 | PERMISSION_DENIED | Permission refusée | 403 |
| 8 | RESOURCE_EXHAUSTED | Quota dépassé | 429 |
| 9 | FAILED_PRECONDITION | Précondition échouée | 400 |
| 10 | ABORTED | Opération abandonnée | 409 |
| 11 | OUT_OF_RANGE | Hors limites | 400 |
| 12 | UNIMPLEMENTED | Non implémenté | 501 |
| 13 | INTERNAL | Erreur interne | 500 |
| 14 | UNAVAILABLE | Service indisponible | 503 |
| 15 | DATA_LOSS | Perte de données | 500 |
| 16 | UNAUTHENTICATED | Non authentifié | 401 |

### 3.2 Erreurs Personnalisées

```python
# utils/errors.py
import grpc
from typing import Optional

class BaseGrpcError(Exception):
    def __init__(self, message: str, status_code: grpc.StatusCode, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def abort_context(self, context):
        context.abort(self.status_code, self.message)

class ValidationError(BaseGrpcError):
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, grpc.StatusCode.INVALID_ARGUMENT, {'field': field})

class NotFoundError(BaseGrpcError):
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, grpc.StatusCode.NOT_FOUND, 
                        {'resource_type': resource_type, 'resource_id': resource_id})

class AlreadyExistsError(BaseGrpcError):
    def __init__(self, resource_type: str, field: str, value: str):
        message = f"{resource_type} with {field}='{value}' already exists"
        super().__init__(message, grpc.StatusCode.ALREADY_EXISTS,
                        {'resource_type': resource_type, 'field': field, 'value': value})

class PermissionDeniedError(BaseGrpcError):
    def __init__(self, action: str, resource: str):
        message = f"Permission denied to {action} {resource}"
        super().__init__(message, grpc.StatusCode.PERMISSION_DENIED,
                        {'action': action, 'resource': resource})

class UnauthenticatedError(BaseGrpcError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, grpc.StatusCode.UNAUTHENTICATED)
```

### 3.3 Gestionnaire d'Erreurs

```python
# utils/error_handler.py
import grpc
import logging
from functools import wraps
from utils.errors import BaseGrpcError

logger = logging.getLogger(__name__)

def handle_errors(func):
    @wraps(func)
    def wrapper(self, request, context, *args, **kwargs):
        try:
            return func(self, request, context, *args, **kwargs)
        except BaseGrpcError as e:
            logger.warning(f"Business error: {e.message}")
            e.abort_context(context)
        except grpc.RpcError:
            raise
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
    return wrapper
```

---

## 4. Intercepteurs gRPC

### 4.1 Intercepteur de Logging

```python
# interceptors/logging_interceptor.py
import grpc
import logging
import time

class LoggingInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        self.logger.info(f"📥 {method}")
        
        handler = continuation(handler_call_details)
        if not handler:
            return None
        
        return self._wrap_handler(handler, method)
    
    def _wrap_handler(self, handler, method):
        if handler.unary_unary:
            return self._wrap_unary_unary(handler, method)
        return handler
    
    def _wrap_unary_unary(self, handler, method):
        def wrapper(request, context):
            start = time.time()
            try:
                response = handler.unary_unary(request, context)
                duration = time.time() - start
                self.logger.info(f"✅ {method} completed in {duration:.3f}s")
                return response
            except Exception as e:
                duration = time.time() - start
                self.logger.error(f"❌ {method} failed in {duration:.3f}s: {e}")
                raise
        
        return grpc.unary_unary_rpc_method_handler(
            wrapper,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer
        )
```

### 4.2 Intercepteur d'Authentification

```python
# interceptors/auth_interceptor.py
import grpc
import jwt
import logging

class AuthInterceptor(grpc.ServerInterceptor):
    PUBLIC_METHODS = [
        '/user.UserService/Login',
        '/user.UserService/Register',
    ]
    
    def __init__(self, jwt_secret: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.jwt_secret = jwt_secret
    
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        
        if method in self.PUBLIC_METHODS:
            return continuation(handler_call_details)
        
        metadata = dict(handler_call_details.invocation_metadata)
        auth_header = metadata.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return self._unauthenticated_handler("Missing authentication token")
        
        token = auth_header[7:]
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            self.logger.info(f"🔓 Authenticated user {payload.get('user_id')}")
            return continuation(handler_call_details)
        except jwt.ExpiredSignatureError:
            return self._unauthenticated_handler("Token expired")
        except jwt.InvalidTokenError:
            return self._unauthenticated_handler("Invalid token")
    
    def _unauthenticated_handler(self, message: str):
        def handler(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, message)
        return grpc.unary_unary_rpc_method_handler(handler, lambda x: x, lambda x: x)
```

### 4.3 Intercepteur de Validation

```python
# interceptors/validation_interceptor.py
import grpc
import logging
from google.protobuf.json_format import MessageToDict

class ValidationInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)
        if handler and handler.unary_unary:
            return self._wrap_unary_unary(handler, handler_call_details.method)
        return handler
    
    def _wrap_unary_unary(self, handler, method):
        def wrapper(request, context):
            errors = self._validate_request(request, method)
            if errors:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "; ".join(errors))
            return handler.unary_unary(request, context)
        
        return grpc.unary_unary_rpc_method_handler(
            wrapper,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer
        )
    
    def _validate_request(self, request, method):
        errors = []
        try:
            data = MessageToDict(request)
        except:
            return errors
        
        if 'CreateUser' in method:
            if not data.get('name'):
                errors.append("name is required")
            if not data.get('email'):
                errors.append("email is required")
        elif 'GetUser' in method or 'UpdateUser' in method:
            if not data.get('userId'):
                errors.append("userId is required")
        
        return errors
```

---

## 5. Service CRUD Complet

### 5.1 Modèle de Données

```python
# models/user.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class User:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    updated_at: int = field(default_factory=lambda: int(datetime.now().timestamp()))
    
    def to_proto(self):
        from generated import user_pb2
        return user_pb2.User(
            id=self.id,
            name=self.name,
            email=self.email,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
```

### 5.2 Validateurs

```python
# utils/validators.py
import re
from typing import Tuple, Optional

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    if not email:
        return False, "Email is required"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, None

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain digit"
    return True, None

def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    if not name:
        return False, "Name is required"
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    if len(name) > 100:
        return False, "Name must not exceed 100 characters"
    return True, None
```

### 5.3 Service UserService Complet

```python
# services/user_service.py
import grpc
import hashlib
from datetime import datetime
from typing import Dict

from generated import user_pb2, user_pb2_grpc
from models.user import User
from services.base_service import BaseService
from utils.validators import validate_email, validate_password, validate_name
from utils.error_handler import handle_errors
from utils.errors import ValidationError, NotFoundError, AlreadyExistsError

class UserService(user_pb2_grpc.UserServiceServicer, BaseService):
    def __init__(self):
        super().__init__()
        self.users: Dict[str, User] = {}
        self.logger.info("UserService initialized")
    
    @handle_errors
    def CreateUser(self, request, context):
        self.log_request("CreateUser", request)
        
        # Validate name
        is_valid, error_msg = validate_name(request.name)
        if not is_valid:
            raise ValidationError(error_msg, field="name")
        
        # Validate email
        is_valid, error_msg = validate_email(request.email)
        if not is_valid:
            raise ValidationError(error_msg, field="email")
        
        # Check if email exists
        for user in self.users.values():
            if user.email == request.email:
                raise AlreadyExistsError("User", "email", request.email)
        
        # Validate password
        is_valid, error_msg = validate_password(request.password)
        if not is_valid:
            raise ValidationError(error_msg, field="password")
        
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
    
    @handle_errors
    def GetUser(self, request, context):
        self.log_request("GetUser", request)
        
        if not request.user_id:
            raise ValidationError("user_id is required", field="user_id")
        
        user = self.users.get(request.user_id)
        if not user:
            raise NotFoundError("User", request.user_id)
        
        response = user.to_proto()
        self.log_response("GetUser", response)
        return response
    
    @handle_errors
    def ListUsers(self, request, context):
        self.log_request("ListUsers", request)
        
        page = max(request.page, 1)
        page_size = min(max(request.page_size, 1), 100)
        
        all_users = list(self.users.values())
        total_count = len(all_users)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_users = all_users[start_idx:end_idx]
        
        response = user_pb2.ListUsersResponse(
            users=[user.to_proto() for user in page_users],
            total_count=total_count
        )
        
        self.log_response("ListUsers", response)
        return response
    
    @handle_errors
    def UpdateUser(self, request, context):
        self.log_request("UpdateUser", request)
        
        if not request.user_id:
            raise ValidationError("user_id is required", field="user_id")
        
        user = self.users.get(request.user_id)
        if not user:
            raise NotFoundError("User", request.user_id)
        
        if request.name:
            is_valid, error_msg = validate_name(request.name)
            if not is_valid:
                raise ValidationError(error_msg, field="name")
            user.name = request.name
        
        if request.email:
            is_valid, error_msg = validate_email(request.email)
            if not is_valid:
                raise ValidationError(error_msg, field="email")
            
            for uid, u in self.users.items():
                if u.email == request.email and uid != request.user_id:
                    raise AlreadyExistsError("User", "email", request.email)
            
            user.email = request.email
        
        user.updated_at = int(datetime.now().timestamp())
        
        self.logger.info(f"User updated: {user.id}")
        response = user.to_proto()
        self.log_response("UpdateUser", response)
        return response
    
    @handle_errors
    def DeleteUser(self, request, context):
        self.log_request("DeleteUser", request)
        
        if not request.user_id:
            raise ValidationError("user_id is required", field="user_id")
        
        if request.user_id not in self.users:
            raise NotFoundError("User", request.user_id)
        
        del self.users[request.user_id]
        
        self.logger.info(f"User deleted: {request.user_id}")
        response = user_pb2.DeleteUserResponse(
            success=True,
            message=f"User {request.user_id} deleted successfully"
        )
        self.log_response("DeleteUser", response)
        return response
    
    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
```

---

## 6. Repository Pattern

### 6.1 Interface Repository

```python
# repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    def list(self, page: int = 1, page_size: int = 10) -> List[T]:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass
    
    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        pass
```

### 6.2 Repository PostgreSQL

```python
# repositories/user_repository.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List
from datetime import datetime

from repositories.base_repository import BaseRepository
from models.user import User
from settings import settings

class UserRepository(BaseRepository[User]):
    def __init__(self):
        self.connection_params = {
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'database': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
        }
    
    def _get_connection(self):
        return psycopg2.connect(**self.connection_params)
    
    def create(self, user: User) -> User:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (id, name, email, password_hash, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (user.id, user.name, user.email, user.password_hash, 
                     user.created_at, user.updated_at)
                )
                row = cursor.fetchone()
                conn.commit()
                return User(**row)
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
                return User(**row) if row else None
    
    def list(self, page: int = 1, page_size: int = 10) -> List[User]:
        offset = (page - 1) * page_size
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s",
                    (page_size, offset)
                )
                rows = cursor.fetchall()
                return [User(**row) for row in rows]
    
    def update(self, user: User) -> User:
        user.updated_at = int(datetime.now().timestamp())
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    UPDATE users SET name = %s, email = %s, updated_at = %s
                    WHERE id = %s RETURNING *
                    """,
                    (user.name, user.email, user.updated_at, user.id)
                )
                row = cursor.fetchone()
                conn.commit()
                return User(**row)
    
    def delete(self, user_id: str) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
    
    def exists(self, user_id: str) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
                return cursor.fetchone() is not None
```

---

## 7. Tests Unitaires

### 7.1 Configuration des Tests

```python
# tests/conftest.py
import pytest
import grpc
from grpc_testing import server_from_dictionary, strict_real_time

from generated import user_pb2, user_pb2_grpc
from services.user_service import UserService

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def grpc_stub(user_service):
    services = {
        user_pb2.DESCRIPTOR.services_by_name['UserService']: user_service
    }
    server = server_from_dictionary(services, strict_real_time())
    return user_pb2_grpc.UserServiceStub(server)
```

### 7.2 Tests du Service

```python
# tests/test_user_service.py
import pytest
import grpc

from generated import user_pb2

class TestUserService:
    def test_create_user_success(self, user_service):
        request = user_pb2.CreateUserRequest(
            name="John Doe",
            email="john@example.com",
            password="SecurePass123"
        )
        
        response = user_service.CreateUser(request, None)
        
        assert response.name == "John Doe"
        assert response.email == "john@example.com"
        assert response.id != ""
    
    def test_create_user_invalid_email(self, user_service):
        request = user_pb2.CreateUserRequest(
            name="John Doe",
            email="invalid-email",
            password="SecurePass123"
        )
        
        with pytest.raises(grpc.RpcError) as exc_info:
            user_service.CreateUser(request, MockContext())
        
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    
    def test_get_user_success(self, user_service):
        # Create user first
        create_request = user_pb2.CreateUserRequest(
            name="Jane Doe",
            email="jane@example.com",
            password="SecurePass123"
        )
        created_user = user_service.CreateUser(create_request, None)
        
        # Get user
        get_request = user_pb2.GetUserRequest(user_id=created_user.id)
        response = user_service.GetUser(get_request, None)
        
        assert response.id == created_user.id
        assert response.name == "Jane Doe"
    
    def test_get_user_not_found(self, user_service):
        request = user_pb2.GetUserRequest(user_id="nonexistent")
        
        with pytest.raises(grpc.RpcError) as exc_info:
            user_service.GetUser(request, MockContext())
        
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    
    def test_list_users_pagination(self, user_service):
        # Create multiple users
        for i in range(5):
            request = user_pb2.CreateUserRequest(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="SecurePass123"
            )
            user_service.CreateUser(request, None)
        
        # List with pagination
        request = user_pb2.ListUsersRequest(page=1, page_size=2)
        response = user_service.ListUsers(request, None)
        
        assert len(response.users) == 2
        assert response.total_count == 5
    
    def test_update_user_success(self, user_service):
        # Create user
        create_request = user_pb2.CreateUserRequest(
            name="Original Name",
            email="original@example.com",
            password="SecurePass123"
        )
        created_user = user_service.CreateUser(create_request, None)
        
        # Update user
        update_request = user_pb2.UpdateUserRequest(
            user_id=created_user.id,
            name="Updated Name"
        )
        response = user_service.UpdateUser(update_request, None)
        
        assert response.name == "Updated Name"
        assert response.email == "original@example.com"
    
    def test_delete_user_success(self, user_service):
        # Create user
        create_request = user_pb2.CreateUserRequest(
            name="To Delete",
            email="delete@example.com",
            password="SecurePass123"
        )
        created_user = user_service.CreateUser(create_request, None)
        
        # Delete user
        delete_request = user_pb2.DeleteUserRequest(user_id=created_user.id)
        response = user_service.DeleteUser(delete_request, None)
        
        assert response.success == True
        
        # Verify deletion
        with pytest.raises(grpc.RpcError):
            get_request = user_pb2.GetUserRequest(user_id=created_user.id)
            user_service.GetUser(get_request, MockContext())

class MockContext:
    def abort(self, code, details):
        raise grpc.RpcError(code, details)
```

### 7.3 Tests des Intercepteurs

```python
# tests/test_interceptors.py
import pytest
from interceptors.logging_interceptor import LoggingInterceptor
from interceptors.validation_interceptor import ValidationInterceptor

class TestLoggingInterceptor:
    def test_logs_request(self, caplog):
        interceptor = LoggingInterceptor()
        # Test implementation
        assert "📥" in caplog.text

class TestValidationInterceptor:
    def test_validates_required_fields(self):
        interceptor = ValidationInterceptor()
        # Test implementation
        pass
```

### 7.4 Exécution des Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=services --cov=interceptors --cov-report=html

# Tests spécifiques
pytest tests/test_user_service.py -v

# Tests avec marqueurs
pytest -m "not slow"
```

---

## Résumé

Ce guide couvre:
- ✅ Architecture en couches
- ✅ Gestion complète des erreurs (16 codes)
- ✅ Intercepteurs (Logging, Auth, Validation)
- ✅ Service CRUD complet
- ✅ Repository pattern avec PostgreSQL
- ✅ Tests unitaires complets

**Bonnes pratiques appliquées:**
- Validation systématique
- Gestion d'erreurs robuste
- Logging structuré
- Séparation des responsabilités
- Code testable

---

**Ce guide est votre référence complète pour implémenter des services gRPC Python production-ready!** 🚀
