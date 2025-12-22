# Guide Complet des Best Practices gRPC

**Version 1.0 - 2025**

**Table des Matières**

1. [Design de Schémas Proto](#1-design-de-schémas-proto)
2. [Versioning et Rétrocompatibilité](#2-versioning-et-rétrocompatibilité)
3. [Performance et Optimisation](#3-performance-et-optimisation)
4. [Sécurité en Production](#4-sécurité-en-production)
5. [Testing et Qualité](#5-testing-et-qualité)
6. [Monitoring et Observabilité](#6-monitoring-et-observabilité)
7. [Déploiement et Scalabilité](#7-déploiement-et-scalabilité)
8. [Patterns et Anti-patterns](#8-patterns-et-anti-patterns)

---

## 1. Design de Schémas Proto

### 1.1 Conventions de Nommage

**Services**
```protobuf
// ✅ BON : Nom au singulier, suffixe Service
service UserService {
  rpc GetUser(GetUserRequest) returns (User) {}
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {}
}

service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (Order) {}
}

// ❌ MAUVAIS : Noms incohérents
service Users {
  rpc get(UserReq) returns (UserResp) {}
  rpc list(Req) returns (Resp) {}
}
```

**Messages**
```protobuf
// ✅ BON : PascalCase, noms descriptifs
message User {
  string id = 1;
  string first_name = 2;  // snake_case pour les champs
  string last_name = 3;
  string email_address = 4;
}

message CreateUserRequest {
  string first_name = 1;
  string last_name = 2;
  string email_address = 3;
}

message CreateUserResponse {
  User user = 1;
  string message = 2;
}

// ❌ MAUVAIS : Noms vagues
message Req {
  string n = 1;
  string e = 2;
}
```

**Méthodes RPC**
```protobuf
// ✅ BON : Verbe + Nom
rpc GetUser(GetUserRequest) returns (User) {}
rpc CreateUser(CreateUserRequest) returns (User) {}
rpc UpdateUser(UpdateUserRequest) returns (User) {}
rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse) {}
rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {}
rpc SearchUsers(SearchUsersRequest) returns (SearchUsersResponse) {}

// ❌ MAUVAIS : Noms non standards
rpc get(Req) returns (Resp) {}
rpc add(UserData) returns (Result) {}
```

### 1.2 Structure des Messages

**Principe de responsabilité unique**
```protobuf
// ✅ BON : Un message = une responsabilité
message User {
  string id = 1;
  string name = 2;
  string email = 3;
}

message Address {
  string street = 1;
  string city = 2;
  string country = 3;
  string postal_code = 4;
}

message UserProfile {
  User user = 1;
  Address address = 2;
  repeated string phone_numbers = 3;
}

// ❌ MAUVAIS : Tout dans un seul message
message UserEverything {
  string id = 1;
  string name = 2;
  string email = 3;
  string street = 4;
  string city = 5;
  string country = 6;
  // ... 50 champs
}
```

**Profondeur d'imbrication**
```protobuf
// ✅ BON : Maximum 3 niveaux
message Order {
  string id = 1;
  Customer customer = 2;  // Niveau 1
  repeated OrderItem items = 3;  // Niveau 1
}

message Customer {
  string id = 1;
  Address address = 2;  // Niveau 2
}

message Address {
  string street = 1;  // Niveau 3
  string city = 2;
}

// ❌ MAUVAIS : Trop d'imbrication
message DeepNested {
  Level1 level1 = 1;
}
message Level1 {
  Level2 level2 = 1;
}
message Level2 {
  Level3 level3 = 1;
}
message Level3 {
  Level4 level4 = 1;
}
// ... Niveau 5, 6, 7...
```

### 1.3 Gestion des Champs

**Types de champs**
```protobuf
message Product {
  // Champs scalaires
  string id = 1;                    // Identifiant unique
  string name = 2;                  // Obligatoire
  string description = 3;           // Optionnel (vide par défaut en proto3)
  double price = 4;                 // Nombre décimal
  int32 stock = 5;                  // Entier 32 bits
  int64 created_at = 6;             // Timestamp (epoch)
  
  // Collections
  repeated string tags = 7;         // Liste
  repeated string categories = 8;   // Liste
  
  // Map
  map<string, string> metadata = 9; // Dictionnaire
  
  // Message imbriqué
  Supplier supplier = 10;           // Objet complexe
  
  // Enum
  Status status = 11;               // Énumération
  
  // Oneof (alternatives mutuelles)
  oneof discount {
    double percentage_discount = 12;
    double fixed_amount_discount = 13;
  }
}

enum Status {
  STATUS_UNSPECIFIED = 0;  // Toujours définir valeur 0
  STATUS_ACTIVE = 1;
  STATUS_INACTIVE = 2;
  STATUS_DISCONTINUED = 3;
}

message Supplier {
  string id = 1;
  string name = 2;
  string contact_email = 3;
}
```

**Valeurs par défaut**
```protobuf
// En proto3, tous les champs ont des valeurs par défaut :
// - string : ""
// - int32/int64 : 0
// - double/float : 0.0
// - bool : false
// - repeated : []
// - map : {}
// - message : null

message User {
  string name = 1;      // Défaut: ""
  int32 age = 2;        // Défaut: 0
  bool is_active = 3;   // Défaut: false
}

// Pour distinguer "non défini" de "valeur par défaut", utiliser wrapper types
import "google/protobuf/wrappers.proto";

message User {
  google.protobuf.StringValue name = 1;  // null si non défini, "" si vide
  google.protobuf.Int32Value age = 2;    // null si non défini, 0 si zéro
  google.protobuf.BoolValue is_active = 3; // null si non défini
}
```

### 1.4 Services et Méthodes

**Principe RESTful adapté à gRPC**
```protobuf
service UserService {
  // CRUD operations
  rpc CreateUser(CreateUserRequest) returns (User) {}
  rpc GetUser(GetUserRequest) returns (User) {}
  rpc UpdateUser(UpdateUserRequest) returns (User) {}
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse) {}
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {}
  
  // Actions spécifiques
  rpc ActivateUser(ActivateUserRequest) returns (User) {}
  rpc DeactivateUser(DeactivateUserRequest) returns (User) {}
  rpc ResetPassword(ResetPasswordRequest) returns (ResetPasswordResponse) {}
}
```

**Nommage des requêtes et réponses**
```protobuf
// Pattern : <Méthode>Request / <Méthode>Response

// ✅ BON
rpc GetUser(GetUserRequest) returns (User) {}  // Réponse = entité
rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse) {}  // Réponse = confirmation

message GetUserRequest {
  string user_id = 1;
}

message DeleteUserRequest {
  string user_id = 1;
}

message DeleteUserResponse {
  bool success = 1;
  string message = 2;
}

// ❌ MAUVAIS : Noms incohérents
rpc GetUser(UserRequest) returns (UserData) {}
rpc DeleteUser(DelReq) returns (Result) {}
```

### 1.5 Documentation

**Commentaires inline**
```protobuf
// Service de gestion des utilisateurs
// Permet de créer, lire, mettre à jour et supprimer des utilisateurs
service UserService {
  // Récupère un utilisateur par son ID
  // Retourne NOT_FOUND si l'utilisateur n'existe pas
  rpc GetUser(GetUserRequest) returns (User) {}
  
  // Crée un nouvel utilisateur
  // Retourne ALREADY_EXISTS si l'email existe déjà
  // Retourne INVALID_ARGUMENT si les données sont invalides
  rpc CreateUser(CreateUserRequest) returns (User) {}
}

// Représente un utilisateur du système
message User {
  // Identifiant unique (UUID v4)
  string id = 1;
  
  // Nom complet de l'utilisateur (2-100 caractères)
  string name = 2;
  
  // Adresse email (format valide requis)
  string email = 3;
  
  // Timestamp de création (Unix epoch en secondes)
  int64 created_at = 4;
  
  // Timestamp de dernière modification
  int64 updated_at = 5;
}
```

### 1.6 Checklist Design Proto

Avant de valider un fichier .proto :

- [ ] Nommage cohérent (PascalCase services/messages, snake_case champs)
- [ ] Pas de mots réservés utilisés comme noms
- [ ] Documentation inline pour services et messages importants
- [ ] Versioning prévu (package v1, v2)
- [ ] Compatibilité descendante respectée
- [ ] Enum avec valeur 0 définie (UNSPECIFIED)
- [ ] Messages de requête/réponse bien nommés
- [ ] Profondeur d'imbrication < 4 niveaux
- [ ] Numéros de champs jamais réutilisés
- [ ] Import des types communs (timestamp, empty, etc.)

---

## 2. Versioning et Rétrocompatibilité

### 2.1 Stratégies de Versioning

**Option 1 : Package versioning (RECOMMANDÉ)**
```protobuf
// v1/user.proto
syntax = "proto3";
package myapi.v1;

service UserService {
  rpc GetUser(GetUserRequest) returns (User) {}
}

message User {
  string id = 1;
  string name = 2;
}

// v2/user.proto
syntax = "proto3";
package myapi.v2;

service UserService {
  rpc GetUser(GetUserRequest) returns (User) {}
  rpc GetUserProfile(GetUserProfileRequest) returns (UserProfile) {}  // Nouveau
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;  // Nouveau champ
}

message UserProfile {  // Nouveau message
  User user = 1;
  repeated string interests = 2;
}
```

**Option 2 : Service versioning**
```protobuf
syntax = "proto3";
package myapi;

service UserServiceV1 {
  rpc GetUser(GetUserRequest) returns (UserV1) {}
}

service UserServiceV2 {
  rpc GetUser(GetUserRequest) returns (UserV2) {}
  rpc GetUserProfile(GetUserProfileRequest) returns (UserProfile) {}
}

message UserV1 {
  string id = 1;
  string name = 2;
}

message UserV2 {
  string id = 1;
  string name = 2;
  string email = 3;
}
```

**Option 3 : Field versioning (DÉCONSEILLÉ)**
```protobuf
// ❌ MAUVAIS : Difficile à maintenir
message User {
  string id = 1;
  string name = 2;
  string email_v2 = 3;
  string phone_v3 = 4;
}
```

### 2.2 Règles de Compatibilité

**Changements SAFE (compatibles)**

✅ **Ajouter nouveaux champs optionnels**
```protobuf
// Version 1
message User {
  string id = 1;
  string name = 2;
}

// Version 2 - SAFE
message User {
  string id = 1;
  string name = 2;
  string email = 3;        // Nouveau champ OK
  int32 age = 4;           // Nouveau champ OK
}
```

✅ **Ajouter nouvelles méthodes RPC**
```protobuf
// Version 1
service UserService {
  rpc GetUser(GetUserRequest) returns (User) {}
}

// Version 2 - SAFE
service UserService {
  rpc GetUser(GetUserRequest) returns (User) {}
  rpc UpdateUser(UpdateUserRequest) returns (User) {}  // Nouveau RPC OK
}
```

✅ **Ajouter nouvelles valeurs enum (avec UNSPECIFIED)**
```protobuf
// Version 1
enum Status {
  STATUS_UNSPECIFIED = 0;
  STATUS_ACTIVE = 1;
  STATUS_INACTIVE = 2;
}

// Version 2 - SAFE
enum Status {
  STATUS_UNSPECIFIED = 0;
  STATUS_ACTIVE = 1;
  STATUS_INACTIVE = 2;
  STATUS_PENDING = 3;      // Nouvelle valeur OK
  STATUS_ARCHIVED = 4;     // Nouvelle valeur OK
}
```

**Changements BREAKING (incompatibles)**

❌ **Supprimer ou renommer champs**
```protobuf
// Version 1
message User {
  string id = 1;
  string name = 2;
  string email = 3;
}

// Version 2 - BREAKING CHANGE!
message User {
  string id = 1;
  string full_name = 2;  // ❌ Renommé, clients anciens cassés!
  // email supprimé       // ❌ Supprimé, clients anciens cassés!
}
```

❌ **Changer le type d'un champ**
```protobuf
// Version 1
message User {
  int32 age = 1;
}

// Version 2 - BREAKING CHANGE!
message User {
  string age = 1;  // ❌ Type changé, incompatible!
}
```

❌ **Changer repeated ↔ non-repeated**
```protobuf
// Version 1
message User {
  string email = 1;
}

// Version 2 - BREAKING CHANGE!
message User {
  repeated string email = 1;  // ❌ Incompatible!
}
```

❌ **Renommer méthodes RPC**
```protobuf
// Version 1
service UserService {
  rpc GetUser(GetUserRequest) returns (User) {}
}

// Version 2 - BREAKING CHANGE!
service UserService {
  rpc FetchUser(GetUserRequest) returns (User) {}  // ❌ Ancien nom cassé!
}
```

### 2.3 Migration Progressive

**Supporter plusieurs versions simultanément**
```python
# backend/server.py
from concurrent import futures
import grpc

from v1 import user_pb2_grpc as user_v1_grpc
from v1.user_service import UserServiceV1

from v2 import user_pb2_grpc as user_v2_grpc
from v2.user_service import UserServiceV2

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Enregistrer V1
    user_v1_grpc.add_UserServiceServicer_to_server(
        UserServiceV1(), server
    )
    
    # Enregistrer V2
    user_v2_grpc.add_UserServiceServicer_to_server(
        UserServiceV2(), server
    )
    
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

**Router basé sur la version**
```python
class VersionRouter:
    def __init__(self):
        self.v1_service = UserServiceV1()
        self.v2_service = UserServiceV2()
    
    def route(self, request, context):
        # Extraire version des metadata
        metadata = dict(context.invocation_metadata())
        version = metadata.get('api-version', 'v1')
        
        if version == 'v2':
            return self.v2_service
        else:
            return self.v1_service
```

### 2.4 Deprecated Fields
```protobuf
message User {
  string id = 1;
  string name = 2;
  
  // ⚠️ Déprécié : Utiliser 'email' à la place
  string old_email = 3 [deprecated = true];
  
  string email = 4;
}

service UserService {
  // ⚠️ Déprécié : Utiliser GetUserV2 à la place
  rpc GetUser(GetUserRequest) returns (User) {
    option deprecated = true;
  }
  
  rpc GetUserV2(GetUserRequestV2) returns (UserV2) {}
}
```

**Gérer les champs dépréciés en code**
```python
def CreateUser(self, request, context):
    # Supporter ancien champ pour rétrocompatibilité
    email = request.email if request.email else request.old_email
    
    if request.HasField('old_email'):
        logging.warning(
            "Field 'old_email' is deprecated. Use 'email' instead."
        )
    
    user = User(
        id=generate_id(),
        name=request.name,
        email=email
    )
    
    return user
```

### 2.5 Reserved Fields

**Réserver numéros et noms pour éviter réutilisation**
```protobuf
message User {
  reserved 3, 5 to 10;              // Numéros réservés
  reserved "old_field", "removed";  // Noms réservés
  
  string id = 1;
  string name = 2;
  string email = 4;
  // 3 est réservé, ne peut pas être réutilisé
  // 5-10 sont réservés
}
```

---

## 3. Performance et Optimisation

### 3.1 Taille des Messages

**Limiter la taille**
```protobuf
// ✅ BON : Messages < 1 MB
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  string bio = 4;  // Limité à 500 caractères côté validation
}

// ❌ MAUVAIS : Message trop large
message UserWithEverything {
  string id = 1;
  bytes profile_picture = 2;  // ❌ Peut être >10 MB!
  bytes video = 3;            // ❌ Peut être >100 MB!
  repeated LogEntry logs = 4; // ❌ Peut être millions d'entrées!
}

// ✅ Solution : Streaming ou pagination
message User {
  string id = 1;
  string name = 2;
  string profile_picture_url = 3;  // URL vers stockage externe
}

service UserService {
  // Pour grandes données, utiliser streaming
  rpc GetUserLogs(GetUserLogsRequest) returns (stream LogEntry) {}
}
```

**Compression automatique**
gRPC compresse automatiquement avec gzip, mais on peut optimiser :
```python
# Python : Configurer compression
import grpc

# Serveur
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    compression=grpc.Compression.Gzip  # Compression activée
)

# Client
channel = grpc.insecure_channel(
    'localhost:50051',
    options=[
        ('grpc.default_compression_algorithm', grpc.Compression.Gzip),
        ('grpc.grpc.default_compression_level', grpc.Compression.High)
    ]
)
```

### 3.2 Connection Pooling

**Réutiliser les channels**
```python
# ✅ BON : Channel réutilisé
class UserClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = UserServiceStub(self.channel)
    
    def get_user(self, user_id):
        request = GetUserRequest(user_id=user_id)
        return self.stub.GetUser(request)
    
    def create_user(self, name, email):
        request = CreateUserRequest(name=name, email=email)
        return self.stub.CreateUser(request)
    
    def close(self):
        self.channel.close()

# Utilisation
client = UserClient()
user1 = client.get_user("123")
user2 = client.get_user("456")
client.close()

# ❌ MAUVAIS : Nouvelle connection à chaque appel
def get_user(user_id):
    channel = grpc.insecure_channel('localhost:50051')  # ❌ NON!
    stub = UserServiceStub(channel)
    request = GetUserRequest(user_id=user_id)
    response = stub.GetUser(request)
    channel.close()
    return response
```

**Connection pool avancé**
```python
from queue import Queue
import grpc

class ConnectionPool:
    def __init__(self, host, port, pool_size=10):
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            channel = grpc.insecure_channel(f'{host}:{port}')
            stub = UserServiceStub(channel)
            self.pool.put((channel, stub))
    
    def get_connection(self):
        return self.pool.get()
    
    def return_connection(self, connection):
        self.pool.put(connection)
    
    def close_all(self):
        while not self.pool.empty():
            channel, _ = self.pool.get()
            channel.close()

# Utilisation
pool = ConnectionPool('localhost', 50051, pool_size=5)

def get_user(user_id):
    channel, stub = pool.get_connection()
    try:
        request = GetUserRequest(user_id=user_id)
        response = stub.GetUser(request)
        return response
    finally:
        pool.return_connection((channel, stub))
```

### 3.3 Batching

**Grouper les requêtes**
```protobuf
// ❌ MAUVAIS : N appels pour N utilisateurs
rpc GetUser(GetUserRequest) returns (User) {}

// Nécessite N appels réseau :
for user_id in user_ids:
    user = stub.GetUser(GetUserRequest(user_id=user_id))

// ✅ BON : Batch request
rpc GetUsers(GetUsersRequest) returns (GetUsersResponse) {}

message GetUsersRequest {
  repeated string user_ids = 1;
}

message GetUsersResponse {
  repeated User users = 1;
}

// 1 seul appel réseau :
response = stub.GetUsers(GetUsersRequest(user_ids=user_ids))
```

**Batch creation**
```protobuf
rpc CreateUsers(CreateUsersRequest) returns (CreateUsersResponse) {}

message CreateUsersRequest {
  repeated CreateUserData users = 1;
}

message CreateUserData {
  string name = 1;
  string email = 2;
}

message CreateUsersResponse {
  repeated User users = 1;
  repeated Error errors = 2;  // Erreurs partielles
}
```

### 3.4 Caching

**Cache côté client**
```python
from functools import lru_cache
from time import time

class CachedUserClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = UserServiceStub(self.channel)
        self.cache = {}
        self.ttl = 300  # 5 minutes
    
    def get_user(self, user_id):
        # Vérifier cache
        if user_id in self.cache:
            cached_data, timestamp = self.cache[user_id]
            if time() - timestamp < self.ttl:
                return cached_data
        
        # Cache miss ou expiré
        request = GetUserRequest(user_id=user_id)
        response = self.stub.GetUser(request)
        
        # Mettre en cache
        self.cache[user_id] = (response, time())
        return response
    
    def invalidate_cache(self, user_id):
        if user_id in self.cache:
            del self.cache[user_id]
```

**Cache côté serveur (Redis)**
```python
import redis
import json

class UserService(user_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.ttl = 300
    
    def GetUser(self, request, context):
        # Vérifier cache Redis
        cache_key = f"user:{request.user_id}"
        cached = self.redis.get(cache_key)
        
        if cached:
            # Cache hit
            data = json.loads(cached)
            return user_pb2.User(**data)
        
        # Cache miss - récupérer de la DB
        user = self.db.get_user(request.user_id)
        
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        
        # Mettre en cache
        self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps({
                'id': user.id,
                'name': user.name,
                'email': user.email
            })
        )
        
        return user
    
    def UpdateUser(self, request, context):
        # Mettre à jour DB
        user = self.db.update_user(request.user_id, request.name, request.email)
        
        # Invalider cache
        cache_key = f"user:{request.user_id}"
        self.redis.delete(cache_key)
        
        return user
```

### 3.5 Timeouts et Deadlines

**Définir des timeouts**
```python
# Client avec timeout
response = stub.GetUser(request, timeout=5.0)  # 5 secondes

# Timeout dans metadata
metadata = [('timeout', '5s')]
response = stub.GetUser(request, metadata=metadata)

# Deadline (temps absolu)
import time
deadline = time.time() + 5
response = stub.GetUser(request, deadline=deadline)
```

**Propager deadlines**
```python
class ProxyService(proxy_pb2_grpc.ProxyServiceServicer):
    def __init__(self):
        self.user_stub = UserServiceStub(...)
    
    def GetUserProxy(self, request, context):
        # Propager deadline du client au service backend
        deadline = context.time_remaining()
        
        try:
            response = self.user_stub.GetUser(
                GetUserRequest(user_id=request.user_id),
                timeout=deadline
            )
            return response
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                context.abort(
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    "Upstream service timeout"
                )
```

### 3.6 Benchmarking

**Outils de benchmark**
```bash
# ghz - gRPC benchmarking tool
ghz --insecure \
  --proto user.proto \
  --call user.UserService/GetUser \
  -d '{"user_id":"123"}' \
  -n 10000 \
  -c 100 \
  localhost:50051

# Résultats :
# Requests:      10000
# Duration:      2.5s
# RPS:           4000
# Average:       25ms
# 50th %ile:     22ms
# 95th %ile:     45ms
# 99th %ile:     78ms
```

**Profiling Python**
```python
import cProfile
import pstats

def benchmark():
    client = UserClient()
    for i in range(1000):
        client.get_user(f"user_{i}")
    client.close()

# Profiler
cProfile.run('benchmark()', 'profile_stats')

# Analyser
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative')
p.print_stats(20)
```

---

## 4. Sécurité en Production

### 4.1 TLS Obligatoire

**Configuration TLS serveur**
```python
import grpc
from concurrent import futures

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # ✅ PRODUCTION : TLS activé
    with open('server.key', 'rb') as f:
        private_key = f.read()
    with open('server.crt', 'rb') as f:
        certificate_chain = f.read()
    with open('ca.crt', 'rb') as f:
        root_certificates = f.read()
    
    server_credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)],
        root_certificates=root_certificates,
        require_client_auth=True  # mTLS
    )
    
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_secure_port('[::]:50051', server_credentials)
    
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

**Configuration TLS client**
```python
import grpc

# ✅ PRODUCTION : TLS avec certificats
with open('ca.crt', 'rb') as f:
    root_certificates = f.read()
with open('client.key', 'rb') as f:
    private_key = f.read()
with open('client.crt', 'rb') as f:
    certificate_chain = f.read()

credentials = grpc.ssl_channel_credentials(
    root_certificates=root_certificates,
    private_key=private_key,
    certificate_chain=certificate_chain
)

channel = grpc.secure_channel('api.example.com:443', credentials)
stub = UserServiceStub(channel)

# ❌ DÉVELOPPEMENT SEULEMENT : Insecure
channel = grpc.insecure_channel('localhost:50051')
```

**Générer certificats**
```bash
# Générer CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 365 -key ca.key -out ca.crt

# Générer certificat serveur
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt

# Générer certificat client
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client.crt
```

### 4.2 Authentification JWT

**Intercepteur d'authentification**
```python
import grpc
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

class AuthInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        self.public_methods = [
            '/user.UserService/Login',
            '/user.UserService/Register'
        ]
    
    def intercept_service(self, continuation, handler_call_details):
        # Méthodes publiques (pas d'auth requise)
        if handler_call_details.method in self.public_methods:
            return continuation(handler_call_details)
        
        # Extraire metadata
        metadata = dict(handler_call_details.invocation_metadata)
        auth_header = metadata.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return self._abort_unauthenticated(
                "Missing or invalid authorization header"
            )
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            # Valider JWT
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Vérifier expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return self._abort_unauthenticated("Token expired")
            
            # Injecter user_id dans context
            return continuation(handler_call_details)
            
        except jwt.InvalidTokenError as e:
            return self._abort_unauthenticated(f"Invalid token: {str(e)}")
    
    def _abort_unauthenticated(self, message):
        def abort(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, message)
        return grpc.unary_unary_rpc_method_handler(abort)

# Utilisation
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    interceptors=[AuthInterceptor()]
)
```

**Générer et valider JWT**
```python
def generate_token(user_id, expiration_hours=24):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

# Service Login
class UserService(user_pb2_grpc.UserServiceServicer):
    def Login(self, request, context):
        # Vérifier credentials
        user = self.db.get_user_by_email(request.email)
        
        if not user or not self.verify_password(request.password, user.password_hash):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials")
        
        # Générer token
        token = generate_token(user.id)
        
        return LoginResponse(
            token=token,
            user=User(id=user.id, name=user.name, email=user.email)
        )
```

**Client avec JWT**
```python
class AuthenticatedClient:
    def __init__(self, host, port):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = UserServiceStub(self.channel)
        self.token = None
    
    def login(self, email, password):
        request = LoginRequest(email=email, password=password)
        response = self.stub.Login(request)
        self.token = response.token
        return response.user
    
    def get_user(self, user_id):
        if not self.token:
            raise Exception("Not authenticated. Call login() first.")
        
        metadata = [('authorization', f'Bearer {self.token}')]
        request = GetUserRequest(user_id=user_id)
        return self.stub.GetUser(request, metadata=metadata)

# Utilisation
client = AuthenticatedClient('localhost', 50051)
client.login('alice@example.com', 'password123')
user = client.get_user('user_123')
```

### 4.3 Validation des Entrées

**TOUJOURS valider côté serveur**
```python
import re
from email_validator import validate_email, EmailNotValidError

class UserService(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        # Validation du nom
        if not request.name or len(request.name) < 2:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Name must be at least 2 characters"
            )
        
        if len(request.name) > 100:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Name must not exceed 100 characters"
            )
        
        # Validation de l'email
        try:
            valid = validate_email(request.email)
            email = valid.email
        except EmailNotValidError as e:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Invalid email: {str(e)}"
            )
        
        # Validation du mot de passe
        if len(request.password) < 8:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Password must be at least 8 characters"
            )
        
        if not re.search(r'[A-Z]', request.password):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Password must contain at least one uppercase letter"
            )
        
        if not re.search(r'[0-9]', request.password):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Password must contain at least one digit"
            )
        
        # Sanitize inputs (prévenir SQL injection, XSS)
        name = self.sanitize(request.name)
        email = self.sanitize(email)
        
        # Créer utilisateur
        user = self.db.create_user(name, email, request.password)
        return user
    
    def sanitize(self, value):
        # Supprimer caractères dangereux
        return re.sub(r'[<>&"\']', '', value)
```

**Intercepteur de validation**
```python
from pydantic import BaseModel, validator

class CreateUserValidator(BaseModel):
    name: str
    email: str
    password: str
    
    @validator('name')
    def name_valid(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Name must be 2-100 characters')
        return v
    
    @validator('email')
    def email_valid(cls, v):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def password_valid(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        return v

class ValidationInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        
        # Map des validateurs par méthode
        validators = {
            '/user.UserService/CreateUser': CreateUserValidator
        }
        
        if method in validators:
            # Valider avant d'appeler le service
            def validated_handler(request, context):
                try:
                    validator = validators[method]
                    validator(**request.__dict__)
                except ValueError as e:
                    context.abort(
                        grpc.StatusCode.INVALID_ARGUMENT,
                        str(e)
                    )
                return continuation(handler_call_details)(request, context)
            
            return grpc.unary_unary_rpc_method_handler(validated_handler)
        
        return continuation(handler_call_details)
```

### 4.4 Rate Limiting

**Intercepteur de rate limiting**
```python
from collections import defaultdict
from time import time

class RateLimitInterceptor(grpc.ServerInterceptor):
    def __init__(self, max_requests=100, window=60):
        self.requests = defaultdict(list)
        self.max_requests = max_requests
        self.window = window  # secondes
    
    def intercept_service(self, continuation, handler_call_details):
        # Extraire client IP
        client_ip = self._get_client_ip(handler_call_details)
        now = time()
        
        # Nettoyer anciennes requêtes (hors fenêtre)
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < self.window
        ]
        
        # Vérifier limite
        if len(self.requests[client_ip]) >= self.max_requests:
            def abort(request, context):
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    f'Rate limit exceeded. Max {self.max_requests} requests per {self.window}s'
                )
            return grpc.unary_unary_rpc_method_handler(abort)
        
        # Enregistrer requête
        self.requests[client_ip].append(now)
        
        return continuation(handler_call_details)
    
    def _get_client_ip(self, handler_call_details):
        # Extraire IP depuis metadata
        metadata = dict(handler_call_details.invocation_metadata)
        return metadata.get('x-forwarded-for', 'unknown')

# Utilisation
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    interceptors=[
        RateLimitInterceptor(max_requests=100, window=60)
    ]
)
```

**Rate limiting avec Redis**
```python
import redis

class RedisRateLimiter:
    def __init__(self, redis_client, max_requests=100, window=60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window
    
    def is_allowed(self, client_id):
        key = f"rate_limit:{client_id}"
        
        # Incrémenter compteur
        count = self.redis.incr(key)
        
        if count == 1:
            # Première requête, définir expiration
            self.redis.expire(key, self.window)
        
        return count <= self.max_requests

class RateLimitInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        self.limiter = RedisRateLimiter(
            redis.Redis(host='localhost', port=6379),
            max_requests=100,
            window=60
        )
    
    def intercept_service(self, continuation, handler_call_details):
        client_ip = self._get_client_ip(handler_call_details)
        
        if not self.limiter.is_allowed(client_ip):
            def abort(request, context):
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    'Rate limit exceeded'
                )
            return grpc.unary_unary_rpc_method_handler(abort)
        
        return continuation(handler_call_details)
```

### 4.5 Secrets Management

**Variables d'environnement**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ BON : Secrets depuis env
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set")

# ❌ MAUVAIS : Secrets en dur
SECRET_KEY = "my-secret-key-123"  # ❌ JAMAIS!
DB_PASSWORD = "password123"       # ❌ JAMAIS!
```

**.env.example**
```env
# Server
SERVER_HOST=[::]
SERVER_PORT=50051

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=grpc_db
DB_USER=postgres
DB_PASSWORD=change-in-production

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=change-in-production

# JWT
JWT_SECRET_KEY=change-in-production-use-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Environment
ENVIRONMENT=production
DEBUG=False
```

**HashiCorp Vault**
```python
import hvac

class VaultSecrets:
    def __init__(self):
        self.client = hvac.Client(url='http://localhost:8200')
        self.client.token = os.getenv('VAULT_TOKEN')
    
    def get_secret(self, path):
        secret = self.client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data']

# Utilisation
vault = VaultSecrets()
db_creds = vault.get_secret('database/postgres')
DB_PASSWORD = db_creds['password']
```

### 4.6 Audit Logging

**Logger toutes les actions sensibles**
```python
import logging
import json
from datetime import datetime

# Configurer logger structuré
import structlog

logger = structlog.get_logger()

class UserService(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        # Extraire metadata
        metadata = dict(context.invocation_metadata())
        client_ip = metadata.get('x-forwarded-for', 'unknown')
        user_agent = metadata.get('user-agent', 'unknown')
        
        # Créer utilisateur
        user = self.db.create_user(request.name, request.email, request.password)
        
        # Audit log
        logger.info(
            "user_created",
            user_id=user.id,
            user_email=user.email,
            client_ip=client_ip,
            user_agent=user_agent,
            timestamp=datetime.utcnow().isoformat()
        )
        
        return user
    
    def DeleteUser(self, request, context):
        metadata = dict(context.invocation_metadata())
        client_ip = metadata.get('x-forwarded-for', 'unknown')
        
        # Supprimer utilisateur
        success = self.db.delete_user(request.user_id)
        
        # Audit log (action sensible!)
        logger.warning(
            "user_deleted",
            user_id=request.user_id,
            client_ip=client_ip,
            success=success,
            timestamp=datetime.utcnow().isoformat()
        )
        
        return DeleteUserResponse(success=success, message="User deleted")
```

**Audit interceptor**
```python
class AuditInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        metadata = dict(handler_call_details.invocation_metadata())
        
        start_time = time.time()
        
        try:
            # Appeler service
            response = continuation(handler_call_details)
            
            # Log succès
            logger.info(
                "rpc_success",
                method=method,
                duration_ms=(time.time() - start_time) * 1000,
                client_ip=metadata.get('x-forwarded-for', 'unknown')
            )
            
            return response
            
        except Exception as e:
            # Log erreur
            logger.error(
                "rpc_error",
                method=method,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
                client_ip=metadata.get('x-forwarded-for', 'unknown')
            )
            raise
```

---

## 5. Testing et Qualité

### 5.1 Pyramide des Tests
```
        /\
       /E2E\      10% - Tests end-to-end
      /------\
     /Intégr.\   30% - Tests d'intégration
    /----------\
   / Unitaires \ 60% - Tests unitaires
  /--------------\
```

**Distribution recommandée:**
- 60% Tests unitaires (rapides, isolés)
- 30% Tests d'intégration (services réels)
- 10% Tests E2E (workflow complet)

### 5.2 Tests Unitaires

**Structure de base**
```python
import pytest
from unittest.mock import Mock, patch
import grpc

from services.user_service import UserService
from generated import user_pb2

@pytest.fixture
def service():
    return UserService()

@pytest.fixture
def context():
    return Mock(spec=grpc.ServicerContext)

def test_get_user_success(service, context):
    # Arrange
    request = user_pb2.GetUserRequest(user_id="123")
    
    # Mock database
    with patch.object(service, 'db') as mock_db:
        mock_db.get_user.return_value = {
            'id': '123',
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        
        # Act
        response = service.GetUser(request, context)
        
        # Assert
        assert response.id == "123"
        assert response.name == "John Doe"
        assert response.email == "john@example.com"
        mock_db.get_user.assert_called_once_with("123")

def test_get_user_not_found(service, context):
    # Arrange
    request = user_pb2.GetUserRequest(user_id="999")
    
    with patch.object(service, 'db') as mock_db:
        mock_db.get_user.return_value = None
        
        # Act & Assert
        with pytest.raises(grpc.RpcError) as exc_info:
            service.GetUser(request, context)
        
        # Vérifier abort appelé avec NOT_FOUND
        context.abort.assert_called_once_with(
            grpc.StatusCode.NOT_FOUND,
            "User not found"
        )

def test_create_user_validation(service, context):
    # Test email invalide
    request = user_pb2.CreateUserRequest(
        name="John",
        email="invalid-email",
        password="password123"
    )
    
    with pytest.raises(grpc.RpcError):
        service.CreateUser(request, context)
    
    context.abort.assert_called_with(
        grpc.StatusCode.INVALID_ARGUMENT,
        pytest.ANY
    )

def test_create_user_already_exists(service, context):
    request = user_pb2.CreateUserRequest(
        name="John",
        email="john@example.com",
        password="password123"
    )
    
    with patch.object(service, 'db') as mock_db:
        mock_db.email_exists.return_value = True
        
        with pytest.raises(grpc.RpcError):
            service.CreateUser(request, context)
        
        context.abort.assert_called_with(
            grpc.StatusCode.ALREADY_EXISTS,
            "Email already exists"
        )
```

**Tests paramétrés**
```python
@pytest.mark.parametrize("name,email,password,expected_error", [
    ("J", "john@example.com", "password123", "Name must be at least 2 characters"),
    ("John", "invalid", "password123", "Invalid email"),
    ("John", "john@example.com", "short", "Password must be at least 8 characters"),
])
def test_create_user_validation_cases(service, context, name, email, password, expected_error):
    request = user_pb2.CreateUserRequest(
        name=name,
        email=email,
        password=password
    )
    
    with pytest.raises(grpc.RpcError):
        service.CreateUser(request, context)
    
    # Vérifier message d'erreur
    args = context.abort.call_args[0]
    assert expected_error in args[1]
```

### 5.3 Tests d'Intégration

**Serveur de test**
```python
import pytest
import grpc
from concurrent import futures

from services.user_service import UserService
from generated import user_pb2_grpc

@pytest.fixture(scope="module")
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(), 
        server
    )
    port = server.add_insecure_port('[::]:0')  # Port random
    server.start()
    
    yield f'localhost:{port}'
    
    server.stop(None)

@pytest.fixture
def grpc_stub(grpc_server):
    channel = grpc.insecure_channel(grpc_server)
    stub = user_pb2_grpc.UserServiceStub(channel)
    yield stub
    channel.close()

def test_create_and_get_user_integration(grpc_stub):
    # Create user
    create_request = user_pb2.CreateUserRequest(
        name="Alice",
        email="alice@example.com",
        password="password123"
    )
    create_response = grpc_stub.CreateUser(create_request)
    
    assert create_response.id is not None
    assert create_response.name == "Alice"
    assert create_response.email == "alice@example.com"
    
    # Get user
    get_request = user_pb2.GetUserRequest(user_id=create_response.id)
    get_response = grpc_stub.GetUser(get_request)
    
    assert get_response.id == create_response.id
    assert get_response.name == "Alice"
    assert get_response.email == "alice@example.com"

def test_user_workflow_integration(grpc_stub):
    # Create
    user = grpc_stub.CreateUser(user_pb2.CreateUserRequest(
        name="Bob",
        email="bob@example.com",
        password="password123"
    ))
    user_id = user.id
    
    # Read
    user = grpc_stub.GetUser(user_pb2.GetUserRequest(user_id=user_id))
    assert user.name == "Bob"
    
    # Update
    user = grpc_stub.UpdateUser(user_pb2.UpdateUserRequest(
        user_id=user_id,
        name="Bob Updated",
        email="bob.updated@example.com"
    ))
    assert user.name == "Bob Updated"
    
    # Delete
    response = grpc_stub.DeleteUser(user_pb2.DeleteUserRequest(user_id=user_id))
    assert response.success is True
    
    # Verify deleted
    with pytest.raises(grpc.RpcError) as exc:
        grpc_stub.GetUser(user_pb2.GetUserRequest(user_id=user_id))
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND
```

### 5.4 Contract Testing

**Vérifier conformité au proto**
```python
def test_create_user_response_contract(grpc_stub):
    request = user_pb2.CreateUserRequest(
        name="Test",
        email="test@example.com",
        password="password123"
    )
    response = grpc_stub.CreateUser(request)
    
    # Vérifier type
    assert isinstance(response, user_pb2.User)
    
    # Vérifier champs obligatoires
    assert hasattr(response, 'id')
    assert hasattr(response, 'name')
    assert hasattr(response, 'email')
    assert hasattr(response, 'created_at')
    assert hasattr(response, 'updated_at')
    
    # Vérifier types de champs
    assert isinstance(response.id, str)
    assert isinstance(response.name, str)
    assert isinstance(response.email, str)
    assert isinstance(response.created_at, int)
    assert isinstance(response.updated_at, int)
    
    # Vérifier valeurs non vides
    assert len(response.id) > 0
    assert len(response.name) > 0
    assert len(response.email) > 0
    assert response.created_at > 0
    assert response.updated_at > 0
```

### 5.5 Coverage

**Configuration pytest avec coverage**
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    --cov=services
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
    --tb=short
```

**Exécuter avec coverage**
```bash
# Tests avec coverage
pytest --cov=services --cov-report=html --cov-report=term

# Résultat attendu :
# Name                    Stmts   Miss  Cover   Missing
# -----------------------------------------------------
# services/__init__.py        0      0   100%
# services/user_service.py  150     15    90%   45-47, 89-92
# -----------------------------------------------------
# TOTAL                     150     15    90%

# Rapport HTML généré dans htmlcov/index.html
```

**Target de coverage:**
- Minimum: 80%
- Recommandé: 90%+
- Code critique (auth, paiement): 100%

### 5.6 Fixtures Avancées

**conftest.py**
```python
# tests/conftest.py
import pytest
import grpc
from concurrent import futures

from services.user_service import UserService
from generated import user_pb2, user_pb2_grpc

@pytest.fixture(scope="session")
def grpc_server():
    """Serveur gRPC pour toute la session de tests"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    port = server.add_insecure_port('[::]:0')
    server.start()
    yield f'localhost:{port}'
    server.stop(None)

@pytest.fixture
def grpc_channel(grpc_server):
    """Channel gRPC réutilisable"""
    channel = grpc.insecure_channel(grpc_server)
    yield channel
    channel.close()

@pytest.fixture
def user_stub(grpc_channel):
    """Stub UserService"""
    return user_pb2_grpc.UserServiceStub(grpc_channel)

@pytest.fixture
def sample_user(user_stub):
    """Utilisateur de test créé avant chaque test"""
    request = user_pb2.CreateUserRequest(
        name="Test User",
        email=f"test_{pytest.test_id}@example.com",
        password="password123"
    )
    user = user_stub.CreateUser(request)
    yield user
    # Cleanup
    try:
        user_stub.DeleteUser(user_pb2.DeleteUserRequest(user_id=user.id))
    except:
        pass

# Utilisation
def test_update_user(user_stub, sample_user):
    # sample_user est déjà créé
    response = user_stub.UpdateUser(user_pb2.UpdateUserRequest(
        user_id=sample_user.id,
        name="Updated Name"
    ))
    assert response.name == "Updated Name"
```

---

## 6. Monitoring et Observabilité

### 6.1 Logging Structuré

**Configuration structlog**
```python
import structlog
import logging

# Configurer structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Utilisation
class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        logger.info(
            "get_user_called",
            user_id=request.user_id,
            method="GetUser",
            service="UserService"
        )
        
        start_time = time.time()
        
        try:
            user = self.db.get_user(request.user_id)
            
            if not user:
                logger.warning(
                    "user_not_found",
                    user_id=request.user_id
                )
                context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
            
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(
                "get_user_success",
                user_id=request.user_id,
                duration_ms=duration_ms
            )
            
            return user
            
        except Exception as e:
            logger.error(
                "get_user_error",
                user_id=request.user_id,
                error=str(e),
                exc_info=True
            )
            raise
```

**Output (JSON)**
```json
{
  "event": "get_user_called",
  "user_id": "123",
  "method": "GetUser",
  "service": "UserService",
  "timestamp": "2025-01-15T10:30:45.123456Z",
  "level": "info"
}
{
  "event": "get_user_success",
  "user_id": "123",
  "duration_ms": 25.5,
  "timestamp": "2025-01-15T10:30:45.148956Z",
  "level": "info"
}
```

### 6.2 Métriques Prometheus

**Intercepteur Prometheus**
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Définir métriques
grpc_requests_total = Counter(
    'grpc_requests_total',
    'Total gRPC requests',
    ['method', 'status']
)

grpc_request_duration_seconds = Histogram(
    'grpc_request_duration_seconds',
    'gRPC request duration in seconds',
    ['method'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

grpc_active_requests = Gauge(
    'grpc_active_requests',
    'Number of active gRPC requests',
    ['method']
)

class PrometheusInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        
        # Incrémenter requests actives
        grpc_active_requests.labels(method=method).inc()
        
        start_time = time.time()
        status = 'success'
        
        try:
            response = continuation(handler_call_details)
            return response
            
        except grpc.RpcError as e:
            status = e.code().name
            raise
            
        finally:
            # Décrémenter requests actives
            grpc_active_requests.labels(method=method).dec()
            
            # Enregistrer durée
            duration = time.time() - start_time
            grpc_request_duration_seconds.labels(method=method).observe(duration)
            
            # Incrémenter compteur
            grpc_requests_total.labels(method=method, status=status).inc()

# Serveur avec métriques
from prometheus_client import start_http_server

def serve():
    # Démarrer serveur métriques Prometheus
    start_http_server(8000)  # Métriques sur :8000/metrics
    
    # Serveur gRPC
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[PrometheusInterceptor()]
    )
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

**Métriques exportées (format Prometheus)**
```
# HELP grpc_requests_total Total gRPC requests
# TYPE grpc_requests_total counter
grpc_requests_total{method="/user.UserService/GetUser",status="success"} 1250
grpc_requests_total{method="/user.UserService/CreateUser",status="success"} 340
grpc_requests_total{method="/user.UserService/GetUser",status="NOT_FOUND"} 15

# HELP grpc_request_duration_seconds gRPC request duration in seconds
# TYPE grpc_request_duration_seconds histogram
grpc_request_duration_seconds_bucket{method="/user.UserService/GetUser",le="0.005"} 120
grpc_request_duration_seconds_bucket{method="/user.UserService/GetUser",le="0.01"} 850
grpc_request_duration_seconds_bucket{method="/user.UserService/GetUser",le="0.025"} 1200
grpc_request_duration_seconds_sum{method="/user.UserService/GetUser"} 15.5
grpc_request_duration_seconds_count{method="/user.UserService/GetUser"} 1250

# HELP grpc_active_requests Number of active gRPC requests
# TYPE grpc_active_requests gauge
grpc_active_requests{method="/user.UserService/GetUser"} 5
```

### 6.3 Distributed Tracing (OpenTelemetry)

**Configuration OpenTelemetry**
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer

# Configurer tracer
resource = Resource(attributes={
    "service.name": "user-service"
})

tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Exporter vers Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

tracer_provider.add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrumenter gRPC automatiquement
GrpcInstrumentorServer().instrument()

# Utilisation dans le code
tracer = trace.get_tracer(__name__)

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        with tracer.start_as_current_span("get_user") as span:
            span.set_attribute("user.id", request.user_id)
            
            # Span pour DB
            with tracer.start_as_current_span("db.get_user"):
                user = self.db.get_user(request.user_id)
            
            if not user:
                span.set_attribute("user.found", False)
                context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
            
            span.set_attribute("user.found", True)
            return user
```

**Traces Jaeger**
```
Trace: get_user [250ms]
├─ get_user (user-service) [250ms]
│  ├─ db.get_user [45ms]
│  │  └─ SQL: SELECT * FROM users [42ms]
│  ├─ cache.check [3ms]
│  └─ response.serialize [2ms]
```

### 6.4 Health Checks

**Service Health**
```python
from grpc_health.v1 import health_pb2, health_pb2_grpc

class HealthServicer(health_pb2_grpc.HealthServicer):
    def __init__(self):
        self.service_status = {}
    
    def Check(self, request, context):
        service = request.service
        
        # Vérifier status du service demandé
        if service == "":
            # Status global
            return health_pb2.HealthCheckResponse(
                status=health_pb2.HealthCheckResponse.SERVING
            )
        
        if service in self.service_status:
            return health_pb2.HealthCheckResponse(
                status=self.service_status[service]
            )
        
        # Service inconnu
        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"Service '{service}' not found"
        )
    
    def Watch(self, request, context):
        # Streaming de status
        service = request.service
        
        while context.is_active():
            yield health_pb2.HealthCheckResponse(
                status=health_pb2.HealthCheckResponse.SERVING
            )
            time.sleep(5)
    
    def set_service_status(self, service, status):
        self.service_status[service] = status

# Ajouter au serveur
health_servicer = HealthServicer()
health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

# Mise à jour status
health_servicer.set_service_status(
    "user.UserService",
    health_pb2.HealthCheckResponse.SERVING
)
```

**Kubernetes Liveness Probe**
```bash
# grpc_health_probe
grpc_health_probe -addr=:50051 -service=user.UserService
```

**kubernetes.yaml**
```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: grpc-service
    image: grpc-service:latest
    ports:
    - containerPort: 50051
    livenessProbe:
      exec:
        command: ["/bin/grpc_health_probe", "-addr=:50051"]
      initialDelaySeconds: 10
      periodSeconds: 10
    readinessProbe:
      exec:
        command: ["/bin/grpc_health_probe", "-addr=:50051", "-service=user.UserService"]
      initialDelaySeconds: 5
      periodSeconds: 5
```

---

## 7. Déploiement et Scalabilité

### 7.1 Docker

**Dockerfile optimisé**
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Generate proto stubs
RUN python -m grpc_tools.protoc \
    -I proto \
    --python_out=generated \
    --grpc_python_out=generated \
    proto/*.proto

# Create non-root user
RUN useradd -m -u 1000 grpcuser && \
    chown -R grpcuser:grpcuser /app

USER grpcuser

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD grpc_health_probe -addr=:50051 || exit 1

EXPOSE 50051

CMD ["python", "server.py"]
```

**Build et run**
```bash
# Build
docker build -t grpc-service:latest .

# Run
docker run -d \
  --name grpc-service \
  -p 50051:50051 \
  -e DB_HOST=postgres \
  -e DB_PASSWORD=secret \
  grpc-service:latest

# Logs
docker logs -f grpc-service

# Stop
docker stop grpc-service
```

### 7.2 Docker Compose

**docker-compose.yml**
```yaml
version: '3.8'

services:
  grpc-server:
    build: ./backend
    ports:
      - "50051:50051"
      - "8000:8000"  # Prometheus metrics
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=grpc_db
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - postgres
      - redis
    networks:
      - grpc-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "grpc_health_probe", "-addr=:50051"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=grpc_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - grpc-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - grpc-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - grpc-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - grpc-network
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  grpc-network:
    driver: bridge
```

**prometheus.yml**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'grpc-service'
    static_configs:
      - targets: ['grpc-server:8000']
```

**Lancer la stack**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f grpc-server

# Scale service
docker-compose up -d --scale grpc-server=3

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### 7.3 Kubernetes

**Deployment**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grpc-service
  labels:
    app: grpc-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: grpc-service
  template:
    metadata:
      labels:
        app: grpc-service
    spec:
      containers:
      - name: grpc-service
        image: grpc-service:latest
        ports:
        - name: grpc
          containerPort: 50051
          protocol: TCP
        - name: metrics
          containerPort: 8000
          protocol: TCP
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: REDIS_HOST
          value: "redis-service"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command: ["/bin/grpc_health_probe", "-addr=:50051"]
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        readinessProbe:
          exec:
            command: ["/bin/grpc_health_probe", "-addr=:50051", "-service=user.UserService"]
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
```

**Service**
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: grpc-service
  labels:
    app: grpc-service
spec:
  type: ClusterIP
  ports:
  - port: 50051
    targetPort: 50051
    protocol: TCP
    name: grpc
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: metrics
  selector:
    app: grpc-service
```

**HorizontalPodAutoscaler**
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: grpc-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: grpc-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max
```

**ConfigMap**
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grpc-config
data:
  SERVER_HOST: "[::]"
  SERVER_PORT: "50051"
  LOG_LEVEL: "INFO"
  DB_PORT: "5432"
  DB_NAME: "grpc_db"
  REDIS_PORT: "6379"
```

**Secret**
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: <base64-encoded-password>
  jwt-secret: <base64-encoded-jwt-secret>
```

**Déployer**
```bash
# Create namespace
kubectl create namespace grpc-app

# Apply configurations
kubectl apply -f configmap.yaml -n grpc-app
kubectl apply -f secret.yaml -n grpc-app
kubectl apply -f deployment.yaml -n grpc-app
kubectl apply -f service.yaml -n grpc-app
kubectl apply -f hpa.yaml -n grpc-app

# View resources
kubectl get all -n grpc-app

# View pods
kubectl get pods -n grpc-app

# View logs
kubectl logs -f deployment/grpc-service -n grpc-app

# Scale manually
kubectl scale deployment grpc-service --replicas=5 -n grpc-app

# View HPA
kubectl get hpa -n grpc-app

# Delete all
kubectl delete namespace grpc-app
```

### 7.4 Load Balancing

**Client-side Load Balancing**
```python
import grpc

# DNS round-robin
channel = grpc.insecure_channel(
    'dns:///grpc-service:50051',
    options=[
        ('grpc.lb_policy_name', 'round_robin'),
        ('grpc.enable_retries', 1),
        ('grpc.service_config', json.dumps({
            "loadBalancingConfig": [{"round_robin": {}}]
        }))
    ]
)
```

**Server-side Load Balancing avec Envoy**
```yaml
# envoy-lb.yaml
static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8080
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          route_config:
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match: { prefix: "/" }
                route:
                  cluster: grpc_cluster
                  timeout: 30s
          http_filters:
          - name: envoy.filters.http.router
  
  clusters:
  - name: grpc_cluster
    connect_timeout: 1s
    type: strict_dns
    lb_policy: round_robin
    http2_protocol_options: {}
    load_assignment:
      cluster_name: grpc_cluster
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: grpc-service
                port_value: 50051
    health_checks:
    - timeout: 1s
      interval: 10s
      unhealthy_threshold: 2
      healthy_threshold: 2
      grpc_health_check: {}
```

---

## 8. Patterns et Anti-patterns

### 8.1 Patterns Recommandés

**Repository Pattern**
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def get(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    def update(self, id: str, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        pass
    
    @abstractmethod
    def list(self, page: int, page_size: int) -> List[T]:
        pass

class UserRepository(BaseRepository[User]):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create(self, user: User) -> User:
        query = """
            INSERT INTO users (id, name, email, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        result = self.db.execute(query, (user.id, user.name, user.email, user.password_hash))
        return User(**result.fetchone())
    
    def get(self, id: str) -> Optional[User]:
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute(query, (id,))
        row = result.fetchone()
        return User(**row) if row else None
    
    # ... autres méthodes

# Service utilise Repository
class UserService(user_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.repository = UserRepository(db_connection)
    
    def GetUser(self, request, context):
        user = self.repository.get(request.user_id)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        return user.to_proto()
```

**Circuit Breaker Pattern**
```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout)
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failures = 0
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.failures >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise e

# Utilisation
breaker = CircuitBreaker()

def get_user_from_external_service(user_id):
    return breaker.call(external_api.get_user, user_id)
```

**Retry avec Backoff Exponentiel**
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except grpc.RpcError as e:
                    if e.code() in [
                        grpc.StatusCode.UNAVAILABLE,
                        grpc.StatusCode.DEADLINE_EXCEEDED
                    ]:
                        retries += 1
                        if retries >= max_retries:
                            raise
                        
                        # Backoff exponentiel
                        delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator

# Utilisation
@retry_with_backoff(max_retries=3)
def get_user(user_id):
    return stub.GetUser(GetUserRequest(user_id=user_id))
```

**Bulkhead Pattern**
```python
from concurrent.futures import ThreadPoolExecutor

class Bulkhead:
    def __init__(self, max_workers=10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute(self, func, *args, **kwargs):
        future = self.executor.submit(func, *args, **kwargs)
        return future.result(timeout=5)

# Isolation par service
user_bulkhead = Bulkhead(max_workers=10)
order_bulkhead = Bulkhead(max_workers=5)

def get_user(user_id):
    return user_bulkhead.execute(stub.GetUser, GetUserRequest(user_id=user_id))

def get_order(order_id):
    return order_bulkhead.execute(order_stub.GetOrder, GetOrderRequest(order_id=order_id))
```

### 8.2 Anti-patterns à Éviter

❌ **Anti-pattern 1: Bloquer le thread avec opérations synchrones**
```python
# ❌ MAUVAIS : Bloquer thread serveur
def GetUser(self, request, context):
    time.sleep(5)  # ❌ Bloque thread!
    return user

# ✅ BON : Opérations asynchrones ou threading
import asyncio

async def GetUser(self, request, context):
    user = await self.db.get_user_async(request.user_id)
    return user
```

❌ **Anti-pattern 2: Pas de timeout**
```python
# ❌ MAUVAIS : Pas de timeout
response = stub.GetUser(request)

# ✅ BON : Toujours définir timeout
response = stub.GetUser(request, timeout=5.0)
```

❌ **Anti-pattern 3: Ignorer les erreurs**
```python
# ❌ MAUVAIS : Ignorer erreurs
try:
    user = stub.GetUser(request)
except:
    pass  # ❌ Silencieux!

# ✅ BON : Gérer explicitement
try:
    user = stub.GetUser(request)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        logger.warning(f"User not found: {request.user_id}")
    else:
        logger.error(f"Error getting user: {e}")
    raise
```

❌ **Anti-pattern 4: Messages trop larges**
```python
# ❌ MAUVAIS : Message énorme
message User {
  bytes profile_picture = 1;  // Peut être 10 MB!
  bytes resume_pdf = 2;       // Peut être 5 MB!
}

# ✅ BON : URLs vers stockage externe
message User {
  string profile_picture_url = 1;
  string resume_url = 2;
}
```

❌ **Anti-pattern 5: Pas de logging/monitoring**
```python
# ❌ MAUVAIS : Aucune visibilité
def GetUser(self, request, context):
    return self.db.get_user(request.user_id)

# ✅ BON : Logging et métriques
def GetUser(self, request, context):
    logger.info("get_user_called", user_id=request.user_id)
    start_time = time.time()
    
    try:
        user = self.db.get_user(request.user_id)
        duration = time.time() - start_time
        logger.info("get_user_success", user_id=request.user_id, duration=duration)
        metrics.record_request("GetUser", "success", duration)
        return user
    except Exception as e:
        logger.error("get_user_error", user_id=request.user_id, error=str(e))
        metrics.record_request("GetUser", "error", time.time() - start_time)
        raise
```

❌ **Anti-pattern 6: Secrets en dur**
```python
# ❌ MAUVAIS : Secrets dans le code
SECRET_KEY = "my-secret-key-123"
DB_PASSWORD = "password123"

# ✅ BON : Variables d'environnement
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

❌ **Anti-pattern 7: Pas de tests**
```python
# ❌ MAUVAIS : Code non testé

# ✅ BON : Tests complets
def test_get_user_success():
    # ...
def test_get_user_not_found():
    # ...
def test_create_user_validation():
    # ...
# Coverage: 85%
```

---

## Annexes

### Annexe A : Checklist Pré-Production

**Code**
- [ ] Tous les tests passent (coverage > 80%)
- [ ] Pas de secrets en dur dans le code
- [ ] Logging configuré (niveau INFO ou WARNING)
- [ ] Gestion d'erreurs complète
- [ ] Validation des entrées côté serveur
- [ ] Pas de code commenté/dead code

**Sécurité**
- [ ] TLS activé (certificats valides)
- [ ] Authentification implémentée (JWT ou autre)
- [ ] Rate limiting configuré
- [ ] Validation des entrées
- [ ] Secrets dans variables d'environnement ou Vault
- [ ] Audit logging activé

**Performance**
- [ ] Connection pooling configuré
- [ ] Timeouts définis sur toutes les requêtes
- [ ] Caching implémenté (si applicable)
- [ ] Messages < 1 MB
- [ ] Benchmarks réalisés

**Monitoring**
- [ ] Métriques Prometheus exportées
- [ ] Logging structuré (JSON)
- [ ] Distributed tracing configuré (Jaeger/Zipkin)
- [ ] Health checks implémentés
- [ ] Dashboards Grafana créés

**Infrastructure**
- [ ] Dockerfile optimisé (multi-stage)
- [ ] docker-compose.yml fonctionnel
- [ ] Kubernetes manifests validés
- [ ] HPA configuré
- [ ] Resource limits définis

**Documentation**
- [ ] README.md complet
- [ ] API documentation à jour
- [ ] Runbook opérationnel
- [ ] Diagrammes d'architecture

### Annexe B : Checklist Sécurité OWASP

**A01 - Broken Access Control**
- [ ] Autorisation vérifiée sur chaque endpoint
- [ ] RBAC implémenté si nécessaire
- [ ] Pas de IDOR (Insecure Direct Object Reference)

**A02 - Cryptographic Failures**
- [ ] TLS 1.3 minimum
- [ ] Pas de données sensibles en clair
- [ ] Passwords hashés (bcrypt, argon2)
- [ ] Clés de chiffrement robustes

**A03 - Injection**
- [ ] Requêtes paramétrées (pas de SQL direct)
- [ ] Validation des entrées
- [ ] Sanitization des outputs

**A04 - Insecure Design**
- [ ] Threat modeling réalisé
- [ ] Principe du moindre privilège
- [ ] Defense in depth

**A05 - Security Misconfiguration**
- [ ] Pas de configurations par défaut
- [ ] Error handling approprié (pas de stack traces exposées)
- [ ] Headers de sécurité configurés

**A06 - Vulnerable Components**
- [ ] Dépendances à jour
- [ ] Scan de vulnérabilités régulier
- [ ] Pas de dépendances deprecated

**A07 - Authentication Failures**
- [ ] JWT avec expiration
- [ ] MFA disponible
- [ ] Rate limiting sur login
- [ ] Pas de credentials par défaut

**A08 - Software and Data Integrity**
- [ ] CI/CD sécurisé
- [ ] Signature de code
- [ ] Vérification intégrité des dépendances

**A09 - Logging Failures**
- [ ] Logging activé
- [ ] Pas de données sensibles dans les logs
- [ ] Alertes sur événements critiques

**A10 - SSRF**
- [ ] Validation des URLs
- [ ] Whitelist de domaines
- [ ] Pas d'accès direct aux métadonnées cloud

### Annexe C : Ressources

**Documentation officielle**
- https://grpc.io
- https://protobuf.dev
- https://grpc.io/docs/languages/python/

**Outils**
- BloomRPC : https://github.com/bloomrpc/bloomrpc
- grpcurl : https://github.com/fullstorydev/grpcurl
- ghz : https://ghz.sh

**Communauté**
- gRPC Slack : https://grpc-slack.herokuapp.com/
- Stack Overflow : https://stackoverflow.com/questions/tagged/grpc
- GitHub : https://github.com/grpc/grpc

---

**Fin du Guide - Version 1.0**

**Auteurs :** Équipe pédagogique gRPC  
**Dernière mise à jour :** Janvier 2025  
**Licence :** CC BY-NC-SA 4.0