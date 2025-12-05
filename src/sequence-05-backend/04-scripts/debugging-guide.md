# Guide de Débogage gRPC Python

## Problèmes Courants

### 1. Erreur "ModuleNotFoundError: No module named 'generated'"

**Cause:** Stubs proto non générés

**Solution:**
```bash
./scripts/generate_proto.sh
# ou
python -m grpc_tools.protoc -I proto --python_out=generated --grpc_python_out=generated proto/*.proto
```

---

### 2. Erreur "module 'user_pb2' has no attribute 'UserServiceServicer'"

**Cause:** Import incorrect ou stubs mal générés

**Solution:**
```python
# Correct:
from generated import user_pb2_grpc

# Incorrect:
from generated import user_pb2
```

---

### 3. Serveur ne démarre pas "Address already in use"

**Cause:** Port 50051 déjà utilisé

**Solution:**
```bash
# Trouver le processus
lsof -i :50051  # macOS/Linux
netstat -ano | findstr :50051  # Windows

# Tuer le processus
kill -9 <PID>

# Ou utiliser un autre port
server.add_insecure_port('[::]:50052')
```

---

### 4. Erreur "StatusCode.UNAVAILABLE"

**Cause:** Client ne peut pas se connecter au serveur

**Solutions:**
- Vérifier que le serveur est démarré
- Vérifier l'adresse (localhost vs 0.0.0.0)
- Vérifier le port
- Vérifier le firewall

```python
# Client
channel = grpc.insecure_channel('localhost:50051')
# Tester la connexion
try:
    grpc.channel_ready_future(channel).result(timeout=5)
    print("Connected!")
except grpc.FutureTimeoutError:
    print("Connection failed")
```

---

### 5. Erreur "StatusCode.UNIMPLEMENTED"

**Cause:** Méthode RPC non implémentée

**Solution:**
```python
class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):  # Implémenter TOUTES les méthodes
        ...
```

---

### 6. Imports relatifs ne fonctionnent pas

**Cause:** Structure de projet ou PYTHONPATH incorrect

**Solution:**
```bash
# À la racine du projet
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python server.py

# Ou utiliser imports absolus
from generated import user_pb2
```

---

## Outils de Débogage

### 1. grpcurl

Tester le serveur en ligne de commande:

```bash
# Lister les services
grpcurl -plaintext localhost:50051 list

# Décrire un service
grpcurl -plaintext localhost:50051 describe user.UserService

# Appeler une méthode
grpcurl -plaintext -d '{"user_id": "123"}' \
  localhost:50051 user.UserService/GetUser
```

### 2. Reflection

Activer la reflection sur le serveur:

```python
from grpc_reflection.v1alpha import reflection

SERVICE_NAMES = (
    user_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
    reflection.SERVICE_NAME,
)
reflection.enable_server_reflection(SERVICE_NAMES, server)
```

### 3. Logging

Configurer des logs détaillés:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,  # Très verbeux
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logs gRPC internes
os.environ['GRPC_VERBOSITY'] = 'DEBUG'
os.environ['GRPC_TRACE'] = 'all'
```

### 4. Python Debugger

Utiliser pdb:

```python
import pdb

def GetUser(self, request, context):
    pdb.set_trace()  # Breakpoint
    user = self.users.get(request.user_id)
    return user
```

### 5. Tests Unitaires

Isoler les problèmes:

```python
def test_get_user():
    service = UserService()
    request = user_pb2.GetUserRequest(user_id="123")
    
    # Mock context si nécessaire
    context = MockContext()
    
    response = service.GetUser(request, context)
    assert response.id == "123"
```

---

## Checklist de Vérification

Avant de demander de l'aide:

- [ ] Stubs proto générés (`ls generated/`)
- [ ] Serveur démarré (`ps aux | grep server.py`)
- [ ] Port correct (50051 par défaut)
- [ ] Imports corrects (`from generated import ...`)
- [ ] Toutes les méthodes RPC implémentées
- [ ] Dépendances installées (`pip list | grep grpc`)
- [ ] Logs consultés
- [ ] Testé avec grpcurl

---

## Messages d'Erreur Fréquents

| Erreur | Signification | Solution |
|--------|---------------|----------|
| INVALID_ARGUMENT | Arguments invalides | Valider les entrées |
| NOT_FOUND | Ressource non trouvée | Vérifier l'ID |
| ALREADY_EXISTS | Ressource existe | Vérifier unicité |
| INTERNAL | Erreur serveur | Consulter les logs |
| UNAUTHENTICATED | Non authentifié | Vérifier le token |
| PERMISSION_DENIED | Permission refusée | Vérifier les droits |

---

## Ressources

- [gRPC Python Docs](https://grpc.io/docs/languages/python/)
- [gRPC Status Codes](https://grpc.github.io/grpc/core/md_doc_statuscodes.html)
- [grpcurl](https://github.com/fullstorydev/grpcurl)

---

**Conseil:** Activez toujours le logging DEBUG pendant le développement!
