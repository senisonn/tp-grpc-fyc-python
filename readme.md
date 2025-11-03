# TP gRPC Python - Service de Logs en Streaming 📡

## Objectif

Ce TP vous permet de découvrir le **Server Streaming** avec gRPC. Vous allez implémenter un service de logs en temps réel, où le serveur envoie continuellement des logs au client, comme un système de monitoring.

## Qu'est-ce que le Server Streaming ?

Contrairement au **Unary RPC** (1 requête → 1 réponse), le **Server Streaming** fonctionne ainsi :
- Le client envoie **1 requête**
- Le serveur renvoie **un flux continu de réponses**

**Cas d'usage** : Logs temps réel, notifications push, flux d'actualités, monitoring de système

### Les 3 Types de Streaming gRPC

#### 1. Server Streaming (ce TP)
```
Client ──[1 requête]──> Serveur
Client <─[réponse 1]─── Serveur
Client <─[réponse 2]─── Serveur
Client <─[réponse 3]─── Serveur
```

#### 2. Client Streaming
```
Client ──[requête 1]──> Serveur
Client ──[requête 2]──> Serveur
Client <─[1 réponse]─── Serveur
```

#### 3. Bidirectional Streaming
```
Client ──[requête 1]──> Serveur
Client <─[réponse 1]─── Serveur
Client ──[requête 2]──> Serveur
Client <─[réponse 2]─── Serveur
```

## Prérequis

- Python 3.7+
- Bibliothèques nécessaires :
  ```bash
  pip install grpcio grpcio-tools
  ```

## Architecture du Projet

```
logs_streaming/
├── logs.proto          # Définition du protocole
├── server.py           # Serveur de logs
├── client.py           # Client qui reçoit les logs
└── README.md
```

---

## 🎯 Travail à Réaliser

### Étape 1 : Définir le fichier Protocol Buffers

Créez un fichier `logs.proto` avec la structure suivante :

#### **Message `LogRequest`** (requête du client)
Le client envoie cette requête pour demander des logs :
- `level` (string) : Niveau de log demandé ("INFO", "WARNING", "ERROR")
- `duration` (int32) : Durée en secondes pendant laquelle recevoir les logs

#### **Message `LogEntry`** (chaque log envoyé par le serveur)
Chaque log contient :
- `timestamp` (string) : Date et heure du log
- `level` (string) : Niveau du log
- `message` (string) : Contenu du log
- `service` (string) : Nom du service qui a généré le log

#### **Service `LogService`**
Définissez une méthode RPC :
```protobuf
rpc StreamLogs(LogRequest) returns (stream LogEntry);
```

⚠️ **Point clé** : Le mot-clé `stream` devant `LogEntry` indique que le serveur va envoyer **plusieurs** messages, pas un seul.

**Indice pour le fichier complet** :
```protobuf
syntax = "proto3";

message LogRequest {
    // À compléter
}

message LogEntry {
    // À compléter
}

service LogService {
    // À compléter
}
```

### Étape 2 : Générer les fichiers Python

Compilez le fichier `.proto` :

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. logs.proto
```

Cela génère :
- `logs_pb2.py` : Classes de messages
- `logs_pb2_grpc.py` : Classes de services

---

### Étape 3 : Implémenter le Serveur

Dans `server.py`, vous devez créer :

#### **Classe `LogServiceServicer`**

Héritez de `logs_pb2_grpc.LogServiceServicer` et implémentez la méthode `StreamLogs`.

**Spécifications** :

1. **Récupérer les paramètres** de la requête (level, duration)

2. **Créer des listes de messages** pour chaque niveau de log :
   - INFO : "Connexion utilisateur réussie", "Requête API traitée", etc.
   - WARNING : "Utilisation mémoire élevée", "Temps de réponse lent", etc.
   - ERROR : "Erreur de connexion DB", "Timeout service externe", etc.

3. **Créer une liste de services** : ["api-gateway", "auth-service", "database", "cache-service", "worker"]

4. **Générer des logs en boucle** :
   - Calculer le timestamp de fin : `end_time = time.time() + request.duration`
   - Tant que `time.time() < end_time` :
     - Choisir un message aléatoire (utilisez `random.choice()`)
     - Créer un objet `LogEntry` avec timestamp, level, message, service
     - **Utiliser `yield` pour envoyer le log** (pas `return` !)
     - Attendre 1 seconde avec `time.sleep(1)`

**Imports nécessaires** :
```python
import grpc
from concurrent import futures
import logs_pb2
import logs_pb2_grpc
import time
from datetime import datetime
import random
```

**Squelette de code** :
```python
class LogServiceServicer(logs_pb2_grpc.LogServiceServicer):
    def StreamLogs(self, request, context):
        # Messages d'exemple
        messages = {
            "INFO": [...],
            "WARNING": [...],
            "ERROR": [...]
        }
        
        services = [...]
        
        end_time = time.time() + request.duration
        
        while time.time() < end_time:
            # Générer un log
            log = logs_pb2.LogEntry(
                timestamp=...,
                level=...,
                message=...,
                service=...
            )
            
            yield log  # ⚠️ CRUCIAL : yield, pas return !
            time.sleep(1)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logs_pb2_grpc.add_LogServiceServicer_to_server(LogServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("🚀 Serveur de logs démarré sur le port 50052")
    server.wait_for_termination()
```

---

### Étape 4 : Implémenter le Client

Dans `client.py`, créez une fonction `stream_logs(level, duration)` :

**Spécifications** :

1. **Se connecter** au serveur sur `localhost:50052`
2. **Créer un stub** du service
3. **Créer et envoyer la requête** avec le niveau et la durée
4. **Itérer sur le flux de réponses** :
   - Utilisez une boucle `for log in stub.StreamLogs(request):`
   - Affichez chaque log au format : `[timestamp] [level] [service] message`
5. **Gérer les erreurs** avec un bloc `try/except`

**Squelette de code** :
```python
import grpc
import logs_pb2
import logs_pb2_grpc

def stream_logs(level, duration):
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = logs_pb2_grpc.LogServiceStub(channel)
        
        request = logs_pb2.LogRequest(level=level, duration=duration)
        
        print(f"📡 Streaming des logs de niveau {level} pendant {duration} secondes...\n")
        
        try:
            for log in stub.StreamLogs(request):
                # Afficher le log
                print(f"[{log.timestamp}] [{log.level}] [{log.service}] {log.message}")
        except grpc.RpcError as e:
            print(f"❌ Erreur gRPC: {e}")

if __name__ == '__main__':
    stream_logs("INFO", 10)
```

**Bonus** : Créez un menu interactif permettant de choisir :
- Le niveau de log (INFO/WARNING/ERROR)
- La durée du streaming
- Plusieurs scénarios pré-configurés

---

## 🚀 Exécution

### 1. Générer les fichiers gRPC

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. logs.proto
```

### 2. Lancer le serveur

```bash
python server.py
```

Sortie attendue :
```
🚀 Serveur de logs démarré sur le port 50052
En attente de connexions...
```

### 3. Lancer le client (dans un autre terminal)

```bash
python client.py
```

Sortie attendue :
```
📡 Streaming des logs de niveau INFO pendant 10 secondes...

[2025-11-03 14:32:01] [INFO] [api-gateway] Connexion utilisateur réussie
[2025-11-03 14:32:02] [INFO] [cache-service] Cache mis à jour
[2025-11-03 14:32:03] [INFO] [database] Requête API traitée
...
✅ Streaming terminé après 10 secondes
```

---

## 🔑 Concepts Clés à Retenir

### 1. Le mot-clé `stream` dans le .proto
```protobuf
rpc StreamLogs(LogRequest) returns (stream LogEntry);
```
- Sans `stream` : le serveur renvoie **1 seul** LogEntry
- Avec `stream` : le serveur renvoie **plusieurs** LogEntry

### 2. `yield` vs `return` dans le serveur
```python
# ❌ FAUX - enverrait tous les logs d'un coup à la fin
def StreamLogs(self, request, context):
    logs = []
    for i in range(10):
        logs.append(log)
    return logs

# ✅ CORRECT - envoie chaque log immédiatement
def StreamLogs(self, request, context):
    for i in range(10):
        yield log  # Envoi immédiat
```

### 3. Itération sur le flux côté client
```python
# Le client reçoit les logs AU FUR ET À MESURE
for log in stub.StreamLogs(request):
    print(log)  # Affiche chaque log dès réception
```

### 4. Différence avec Unary RPC

| Unary RPC | Server Streaming |
|-----------|------------------|
| `response = stub.GetClient(request)` | `for log in stub.StreamLogs(request):` |
| 1 réponse | Plusieurs réponses |
| Client attend la fin | Client reçoit en temps réel |

---

## 🎓 Questions de Compréhension

1. Que se passe-t-il si vous utilisez `return` au lieu de `yield` dans le serveur ?
2. Comment le client sait-il que le streaming est terminé ?
3. Que se passe-t-il si le serveur crash pendant le streaming ?
4. Peut-on avoir plusieurs clients connectés simultanément ? Comment ?
5. Quelle est la différence entre server streaming et polling HTTP classique ?

---

## 🏆 Exercices Bonus

### Niveau 1 : Filtrage par service
- Ajoutez un champ `service_filter` dans `LogRequest`
- Le serveur ne renvoie que les logs du service demandé

### Niveau 2 : Plusieurs niveaux simultanés
- Permettez au client de demander plusieurs niveaux : `["INFO", "WARNING"]`
- Le serveur génère des logs mixtes

### Niveau 3 : Logs depuis un fichier
- Au lieu de logs aléatoires, lisez un vrai fichier de logs ligne par ligne
- Envoyez chaque ligne au client en streaming

### Niveau 4 : Statistiques en fin de streaming
- Après le streaming, le serveur envoie un dernier message avec :
  - Nombre total de logs envoyés
  - Répartition par niveau
  - Temps total écoulé

### Niveau 5 : Limitation de débit
- Ajoutez un paramètre `logs_per_second` dans `LogRequest`
- Le serveur adapte le délai entre chaque log

---

## 📊 Quand utiliser le Server Streaming ?

| ✅ Cas d'usage adaptés | ❌ Cas non adaptés |
|------------------------|-------------------|
| Logs temps réel | Simple requête/réponse |
| Notifications push | Upload de fichier |
| Flux d'actualités | CRUD classique |
| Monitoring de metrics | Authentification |
| Live updates | Opérations atomiques |

---

## ✅ Critères de Validation

Votre TP est réussi si :

- ✅ Le fichier `.proto` est correctement défini avec le mot-clé `stream`
- ✅ Le serveur utilise `yield` pour envoyer les logs
- ✅ Le client affiche les logs **en temps réel** (pas tous à la fin)
- ✅ Le streaming s'arrête après la durée demandée
- ✅ Les logs contiennent timestamp, niveau, message et service
- ✅ Le code gère les erreurs de connexion
- ✅ Plusieurs clients peuvent se connecter simultanément

---

## 📚 Ressources

- [gRPC Server Streaming Documentation](https://grpc.io/docs/what-is-grpc/core-concepts/#server-streaming-rpc)
- [Protocol Buffers Language Guide](https://developers.google.com/protocol-buffers/docs/proto3)
- [Python gRPC Examples](https://github.com/grpc/grpc/tree/master/examples/python)
- [gRPC vs REST vs WebSocket](https://www.baeldung.com/rest-vs-grpc)

---

**Bon streaming ! 🚀📡**