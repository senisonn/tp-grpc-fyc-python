# TP gRPC Python - Sécurisation avec Authentification 🔒

## Objectif

Ce TP vous apprend à **sécuriser un service gRPC** avec un système d'authentification par **JWT (JSON Web Token)**. Vous allez implémenter un service utilisateur où certaines opérations nécessitent une authentification valide.

## Pourquoi sécuriser un service gRPC ?

Par défaut, **tout le monde** peut appeler vos services gRPC. C'est comme laisser la porte de votre maison ouverte ! 🚪

### Problèmes sans authentification :
- ❌ N'importe qui peut accéder aux données sensibles
- ❌ Pas de contrôle sur qui fait quoi
- ❌ Impossible de tracer les actions par utilisateur
- ❌ Vulnérable aux attaques

### Avec authentification :
- ✅ Seuls les utilisateurs authentifiés peuvent accéder aux données
- ✅ Chaque requête est liée à un utilisateur identifié
- ✅ Logs et audit possibles
- ✅ Gestion fine des permissions

## Concepts Clés

### 1. **JWT (JSON Web Token)**
Un token JWT est une chaîne encodée qui contient :
- **Header** : Type de token et algorithme de signature
- **Payload** : Données (user_id, username, expiration)
- **Signature** : Garantit que le token n'a pas été modifié

Exemple de JWT :
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFsaWNlIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### 2. **Metadata dans gRPC**
Les metadata sont comme les **headers HTTP** :
```python
# Client envoie le token
metadata = [('authorization', f'Bearer {token}')]
response = stub.GetProfile(request, metadata=metadata)

# Serveur récupère le token
token = dict(context.invocation_metadata()).get('authorization')
```

### 3. **Interceptors gRPC**
Un interceptor est un **middleware** qui intercepte toutes les requêtes :
```python
Requête client
    ↓
[Interceptor] ← Vérifie le token
    ↓
Service métier
```

Avantage : On n'a pas besoin de vérifier le token dans chaque méthode !

## Prérequis

- Python 3.7+
- Bibliothèques nécessaires :
  ```bash
  pip install grpcio grpcio-tools pyjwt
  pip install --force-reinstall cffi cryptography
  ```

## Architecture du Projet

```
secure_service/
├── user.proto          # Définition du service utilisateur
├── server.py           # Serveur avec authentification
├── client.py           # Client qui s'authentifie
├── auth_interceptor.py # Interceptor pour vérifier les tokens
└── README.md
```

---

## 🎯 Travail à Réaliser

### Étape 1 : Définir le fichier Protocol Buffers

Créez un fichier `user.proto` avec les messages et services suivants :

#### **Messages**

1. **LoginRequest** : Pour se connecter
   - `username` (string)
   - `password` (string)

2. **LoginResponse** : Retour de la connexion
   - `token` (string) : JWT token
   - `user_id` (int32)
   - `message` (string) : Message de succès/erreur

3. **User** : Représente un utilisateur
   - `id` (int32)
   - `username` (string)
   - `email` (string)
   - `full_name` (string)

4. **GetProfileRequest** : Pour récupérer un profil
   - `user_id` (int32)

5. **GetProfileResponse** : Retour du profil
   - `user` (User)
   - `error` (string)

6. **UpdateProfileRequest** : Pour mettre à jour un profil
   - `user_id` (int32)
   - `email` (string)
   - `full_name` (string)

7. **UpdateProfileResponse** : Retour de la mise à jour
   - `success` (bool)
   - `message` (string)

#### **Service UserService**

Définissez 3 méthodes RPC :
```protobuf
service UserService {
    rpc Login(LoginRequest) returns (LoginResponse);           // Pas d'auth nécessaire
    rpc GetProfile(GetProfileRequest) returns (GetProfileResponse);  // Auth requise
    rpc UpdateProfile(UpdateProfileRequest) returns (UpdateProfileResponse);  // Auth requise
}
```

**Squelette** :
```protobuf
syntax = "proto3";

message LoginRequest {
    // À compléter
}

message LoginResponse {
    // À compléter
}

message User {
    // À compléter
}

// Autres messages...

service UserService {
    // À compléter
}
```

### Étape 2 : Générer les fichiers Python

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto
```

---

### Étape 3 : Créer l'Interceptor d'Authentification

Créez un fichier `auth_interceptor.py` qui vérifie les tokens JWT.

#### **Spécifications**

1. **Créer une classe `AuthInterceptor`** qui hérite de `grpc.ServerInterceptor`

2. **Définir une clé secrète** pour signer les JWT :
   ```python
   SECRET_KEY = "votre_cle_secrete_super_secure_123"
   ```

3. **Lister les méthodes publiques** (qui ne nécessitent pas d'auth) :
   ```python
   PUBLIC_METHODS = ['/UserService/Login']
   ```

4. **Implémenter la méthode `intercept_service`** qui :
   - Récupère le nom de la méthode appelée
   - Si la méthode est publique → laisse passer
   - Sinon → récupère le token dans les metadata
   - Vérifie et décode le token JWT
   - Si valide → ajoute les infos utilisateur au context et laisse passer
   - Si invalide → retourne une erreur `PERMISSION_DENIED`

**Imports nécessaires** :
```python
import grpc
import jwt
from datetime import datetime, timedelta
```

**Squelette** :
```python
SECRET_KEY = "votre_cle_secrete"
PUBLIC_METHODS = ['/UserService/Login']

class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method_name = handler_call_details.method
        
        # Si méthode publique, laisser passer
        if method_name in PUBLIC_METHODS:
            return continuation(handler_call_details)
        
        # Récupérer le token
        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get('authorization', '')
        
        if not token.startswith('Bearer '):
            return self._deny_access()
        
        token = token[7:]  # Enlever "Bearer "
        
        try:
            # Vérifier et décoder le token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # TODO: Ajouter les infos au context si besoin
            return continuation(handler_call_details)
        except jwt.ExpiredSignatureError:
            return self._deny_access("Token expiré")
        except jwt.InvalidTokenError:
            return self._deny_access("Token invalide")
    
    def _deny_access(self, message="Non autorisé"):
        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, message)
        return grpc.unary_unary_rpc_method_handler(abort)

def generate_token(user_id, username):
    """Génère un JWT token pour un utilisateur"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Expire dans 1h
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Vérifie un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None
```

---

### Étape 4 : Implémenter le Serveur

Dans `server.py`, créez le service utilisateur sécurisé.

#### **Spécifications**

1. **Base de données simulée** (dictionnaire Python) :
   ```python
   USERS_DB = {
       "alice": {"id": 1, "password": "password123", "email": "alice@example.com", "full_name": "Alice Dupont"},
       "bob": {"id": 2, "password": "secret456", "email": "bob@example.com", "full_name": "Bob Martin"}
   }
   ```

2. **Classe `UserServiceServicer`** avec 3 méthodes :

   **a) `Login(request, context)`** :
   - Vérifie username/password
   - Si correct → génère un token JWT et retourne `LoginResponse`
   - Si incorrect → retourne une erreur

   **b) `GetProfile(request, context)`** :
   - **Protégée par l'interceptor** (token vérifié automatiquement)
   - Récupère les infos de l'utilisateur depuis la DB
   - Retourne `GetProfileResponse`

   **c) `UpdateProfile(request, context)`** :
   - **Protégée par l'interceptor**
   - Met à jour email et full_name dans la DB
   - Retourne `UpdateProfileResponse`

3. **Fonction `serve()`** :
   - Crée le serveur avec l'interceptor
   - Ajoute le service
   - Démarre sur le port 50053

**Squelette** :
```python
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc
from auth_interceptor import AuthInterceptor, generate_token

USERS_DB = {
    "alice": {"id": 1, "password": "password123", "email": "alice@example.com", "full_name": "Alice Dupont"},
    "bob": {"id": 2, "password": "secret456", "email": "bob@example.com", "full_name": "Bob Martin"}
}

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def Login(self, request, context):
        # Vérifier les credentials
        user = USERS_DB.get(request.username)
        
        if not user or user['password'] != request.password:
            return user_pb2.LoginResponse(
                token="",
                user_id=0,
                message="Identifiants incorrects"
            )
        
        # Générer le token
        token = generate_token(user['id'], request.username)
        
        return user_pb2.LoginResponse(
            token=token,
            user_id=user['id'],
            message="Connexion réussie"
        )
    
    def GetProfile(self, request, context):
        # Cette méthode est protégée par l'interceptor
        # Le token a déjà été vérifié !
        
        # Trouver l'utilisateur
        user = None
        for username, data in USERS_DB.items():
            if data['id'] == request.user_id:
                user = data
                break
        
        if not user:
            return user_pb2.GetProfileResponse(error="Utilisateur non trouvé")
        
        user_obj = user_pb2.User(
            id=user['id'],
            username=username,
            email=user['email'],
            full_name=user['full_name']
        )
        
        return user_pb2.GetProfileResponse(user=user_obj, error="")
    
    def UpdateProfile(self, request, context):
        # Protégée par l'interceptor
        
        # Trouver et mettre à jour l'utilisateur
        for username, data in USERS_DB.items():
            if data['id'] == request.user_id:
                data['email'] = request.email
                data['full_name'] = request.full_name
                return user_pb2.UpdateProfileResponse(
                    success=True,
                    message="Profil mis à jour avec succès"
                )
        
        return user_pb2.UpdateProfileResponse(
            success=False,
            message="Utilisateur non trouvé"
        )

def serve():
    # Créer le serveur AVEC l'interceptor
    interceptors = [AuthInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=interceptors  # ← CRUCIAL !
    )
    
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    print("🔒 Serveur sécurisé démarré sur le port 50053")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

---

### Étape 5 : Implémenter le Client

Dans `client.py`, créez un client qui s'authentifie avant d'accéder aux ressources protégées.

#### **Spécifications**

1. **Fonction `login(stub, username, password)`** :
   - Appelle la méthode Login
   - Récupère et retourne le token

2. **Fonction `get_profile(stub, user_id, token)`** :
   - Appelle GetProfile en **passant le token dans les metadata**
   - Affiche le profil

3. **Fonction `update_profile(stub, user_id, email, full_name, token)`** :
   - Appelle UpdateProfile avec le token
   - Affiche le résultat

4. **Fonction `main()`** :
   - Se connecte en tant qu'Alice
   - Récupère son profil
   - Met à jour son profil
   - Teste avec un token invalide

**Squelette** :
```python
import grpc
import user_pb2
import user_pb2_grpc

def login(stub, username, password):
    """Se connecter et obtenir un token"""
    request = user_pb2.LoginRequest(username=username, password=password)
    response = stub.Login(request)
    
    if response.token:
        print(f"✅ Connexion réussie ! Token reçu.")
        print(f"   User ID: {response.user_id}")
        return response.token
    else:
        print(f"❌ {response.message}")
        return None

def get_profile(stub, user_id, token):
    """Récupérer le profil (nécessite authentification)"""
    request = user_pb2.GetProfileRequest(user_id=user_id)
    
    # CRUCIAL : Passer le token dans les metadata
    metadata = [('authorization', f'Bearer {token}')]
    
    try:
        response = stub.GetProfile(request, metadata=metadata)
        
        if response.error:
            print(f"❌ Erreur: {response.error}")
        else:
            print(f"👤 Profil récupéré:")
            print(f"   Username: {response.user.username}")
            print(f"   Email: {response.user.email}")
            print(f"   Nom: {response.user.full_name}")
    except grpc.RpcError as e:
        print(f"❌ Erreur gRPC: {e.code()} - {e.details()}")

def update_profile(stub, user_id, email, full_name, token):
    """Mettre à jour le profil (nécessite authentification)"""
    request = user_pb2.UpdateProfileRequest(
        user_id=user_id,
        email=email,
        full_name=full_name
    )
    
    metadata = [('authorization', f'Bearer {token}')]
    
    try:
        response = stub.UpdateProfile(request, metadata=metadata)
        
        if response.success:
            print(f"✅ {response.message}")
        else:
            print(f"❌ {response.message}")
    except grpc.RpcError as e:
        print(f"❌ Erreur gRPC: {e.code()} - {e.details()}")

def main():
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        
        print("=" * 60)
        print("🔒 CLIENT SÉCURISÉ - TEST D'AUTHENTIFICATION")
        print("=" * 60)
        
        # Test 1 : Login avec bons identifiants
        print("\n[TEST 1] Connexion avec alice...")
        token = login(stub, "alice", "password123")
        
        if token:
            # Test 2 : Récupérer le profil avec token valide
            print("\n[TEST 2] Récupération du profil (avec token)...")
            get_profile(stub, 1, token)
            
            # Test 3 : Mettre à jour le profil
            print("\n[TEST 3] Mise à jour du profil...")
            update_profile(stub, 1, "alice.dupont@example.com", "Alice DUPONT", token)
            
            # Test 4 : Re-vérifier le profil
            print("\n[TEST 4] Vérification après mise à jour...")
            get_profile(stub, 1, token)
        
        # Test 5 : Tenter d'accéder sans token
        print("\n[TEST 5] Tentative sans token (doit échouer)...")
        try:
            get_profile(stub, 1, "")
        except:
            pass
        
        # Test 6 : Token invalide
        print("\n[TEST 6] Token invalide (doit échouer)...")
        try:
            get_profile(stub, 1, "fake_token_123")
        except:
            pass
        
        # Test 7 : Mauvais identifiants
        print("\n[TEST 7] Mauvais mot de passe...")
        login(stub, "alice", "wrong_password")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
```

---

## 🚀 Exécution

### 1. Générer les fichiers gRPC

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto
```

### 2. Lancer le serveur

```bash
python server.py
```

Sortie :
```
🔒 Serveur sécurisé démarré sur le port 50053
```

### 3. Lancer le client

```bash
python client.py
```

Sortie attendue :
```
============================================================
🔒 CLIENT SÉCURISÉ - TEST D'AUTHENTIFICATION
============================================================

[TEST 1] Connexion avec alice...
✅ Connexion réussie ! Token reçu.
   User ID: 1

[TEST 2] Récupération du profil (avec token)...
👤 Profil récupéré:
   Username: alice
   Email: alice@example.com
   Nom: Alice Dupont

[TEST 3] Mise à jour du profil...
✅ Profil mis à jour avec succès

[TEST 4] Vérification après mise à jour...
👤 Profil récupéré:
   Username: alice
   Email: alice.dupont@example.com
   Nom: Alice DUPONT

[TEST 5] Tentative sans token (doit échouer)...
❌ Erreur gRPC: StatusCode.PERMISSION_DENIED - Non autorisé

[TEST 6] Token invalide (doit échouer)...
❌ Erreur gRPC: StatusCode.PERMISSION_DENIED - Token invalide

[TEST 7] Mauvais mot de passe...
❌ Identifiants incorrects
```

---

## 🔑 Concepts Clés Expliqués

### 1. **Flow d'authentification complet**

```
┌────────┐                          ┌────────┐
│ Client │                          │ Server │
└───┬────┘                          └───┬────┘
    │                                   │
    │  Login(username, password)        │
    │──────────────────────────────────>│
    │                                   │ Vérif credentials
    │                                   │ Génère JWT
    │  LoginResponse(token)             │
    │<──────────────────────────────────│
    │                                   │
    │  GetProfile(user_id)              │
    │  + metadata: "Bearer {token}"     │
    │──────────────────────────────────>│
    │                                   │ [Interceptor]
    │                                   │ Vérifie token
    │                                   │ Décode JWT
    │                                   │ ✓ OK
    │  GetProfileResponse(user)         │
    │<──────────────────────────────────│
    │                                   │
```

### 2. **Pourquoi utiliser un Interceptor ?**

**❌ Sans interceptor** :
```python
def GetProfile(self, request, context):
    # Dupliquer ce code dans CHAQUE méthode
    token = dict(context.invocation_metadata()).get('authorization')
    if not verify_token(token):
        context.abort(grpc.StatusCode.PERMISSION_DENIED, "Non autorisé")
    # Logique métier...

def UpdateProfile(self, request, context):
    # Re-dupliquer le code
    token = dict(context.invocation_metadata()).get('authorization')
    if not verify_token(token):
        context.abort(grpc.StatusCode.PERMISSION_DENIED, "Non autorisé")
    # Logique métier...
```

**✅ Avec interceptor** :
```python
# La vérification est centralisée !
def GetProfile(self, request, context):
    # Le token a déjà été vérifié par l'interceptor
    # On peut directement traiter la requête
    # Logique métier...
```

### 3. **Structure d'un JWT**

Un token JWT a 3 parties séparées par des `.` :
```
eyJhbGci...  .  eyJ1c2Vy...  .  SflKxwRJ...
   HEADER        PAYLOAD        SIGNATURE
```

**Header** (encodé en Base64) :
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload** (encodé en Base64) :
```json
{
  "user_id": 1,
  "username": "alice",
  "exp": 1738675200
}
```

**Signature** :
```
HMACSHA256(
  base64(header) + "." + base64(payload),
  SECRET_KEY
)
```

### 4. **Metadata vs Body**

| Metadata | Body (Message) |
|----------|----------------|
| Comme les headers HTTP | Comme le body HTTP |
| Pour infos transversales (auth, tracing) | Pour les données métier |
| `context.invocation_metadata()` | `request.field` |
| Exemple : token, user-agent | Exemple : user_id, email |

---

## 🎓 Questions de Compréhension

1. Pourquoi utilise-t-on JWT plutôt que de stocker les sessions côté serveur ?
2. Que se passe-t-il si le SECRET_KEY est compromis ?
3. Comment gérer le renouvellement des tokens expirés ?
4. Pourquoi l'interceptor est-il plus efficace que vérifier dans chaque méthode ?
5. Comment ajouter des rôles/permissions aux utilisateurs ?

---

## 🏆 Exercices Bonus

### Niveau 1 : Durée de vie personnalisée
- Ajoutez un paramètre `token_duration` dans LoginRequest
- Le serveur génère un token avec la durée demandée

### Niveau 2 : Refresh Token
- Implémentez un système de refresh token
- Le client peut renouveler son token sans re-saisir le mot de passe

### Niveau 3 : Rôles et Permissions
- Ajoutez un champ `role` aux utilisateurs (USER, ADMIN)
- Seuls les ADMIN peuvent appeler UpdateProfile
- Créez un interceptor qui vérifie les permissions

### Niveau 4 : SSL/TLS
- Remplacez `insecure_channel` par un canal sécurisé avec certificats
- Utilisez `grpc.ssl_channel_credentials()`

### Niveau 5 : Rate Limiting
- Limitez le nombre de tentatives de login (3 max par minute)
- Bloquez temporairement l'utilisateur après 5 échecs

### Niveau 6 : Tokens dans Base de Données
- Stockez les tokens actifs en base
- Permettez la révocation de tokens

---

## ⚠️ Sécurité en Production

Ce TP est pédagogique. En production, vous devez :

1. **Ne JAMAIS** stocker les mots de passe en clair
   - Utilisez `bcrypt` ou `argon2`

2. **Ne JAMAIS** hardcoder le SECRET_KEY
   - Utilisez des variables d'environnement

3. **Toujours utiliser SSL/TLS**
   - Pas de `insecure_channel` en prod

4. **Durée de vie courte des tokens**
   - Maximum 15 minutes pour les access tokens
   - Utilisez des refresh tokens

5. **Loguer les tentatives d'accès**
   - Pour détecter les attaques

6. **Valider les entrées**
   - Protégez contre les injections

---

## 📊 Comparaison des Méthodes d'Auth

| Méthode | Avantages | Inconvénients |
|---------|-----------|---------------|
| **JWT** | Sans état, scalable | Révocation difficile |
| **Session** | Révocation facile | Nécessite stockage serveur |
| **mTLS** | Très sécurisé | Complexe à gérer |
| **API Key** | Simple | Moins flexible |
| **OAuth2** | Standard industrie | Complexe à implémenter |

---

## ✅ Critères de Validation

Votre TP est réussi si :

- ✅ Le serveur refuse les requêtes sans token sur les méthodes protégées
- ✅ Login génère un JWT valide
- ✅ L'interceptor vérifie correctement les tokens
- ✅ Les tokens expirés sont rejetés
- ✅ Les tokens invalides retournent PERMISSION_DENIED
- ✅ GetProfile et UpdateProfile fonctionnent avec un token valide
- ✅ Le client gère correctement les erreurs d'authentification

---

## 📚 Ressources

- [JWT.io - Debugger de tokens](https://jwt.io/)
- [gRPC Authentication Guide](https://grpc.io/docs/guides/auth/)
- [Python JWT Library](https://pyjwt.readthedocs.io/)
- [gRPC Interceptors Documentation](https://grpc.github.io/grpc/python/grpc.html#service-side-interceptor)

---

**Bonne sécurisation ! 🔒🚀**