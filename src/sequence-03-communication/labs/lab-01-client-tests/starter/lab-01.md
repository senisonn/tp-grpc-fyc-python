# TP gRPC Python - Service de Gestion de Clients

## Objectif

Ce TP a pour objectif de vous familiariser avec le framework **gRPC** en Python. Vous allez implémenter un service client-serveur simple permettant de récupérer des informations sur un client à partir de son identifiant.

## Prérequis

- Python 3.7+
- Bibliothèques nécessaires :
  ```bash
  pip install grpcio grpcio-tools
  ```

## Architecture du Projet

Le projet se compose de trois fichiers principaux :

- `client.proto` : Définition du protocole gRPC (Protocol Buffers)
- `server.py` : Implémentation du serveur gRPC
- `client.py` : Implémentation du client gRPC
- `client_test.py` : Tests unitaires

## Travail à Réaliser

### Étape 1 : Définir le fichier Protocol Buffers

Créez un fichier `client.proto` qui définit :

- **Message `Client`** avec les champs suivants :
  - `id` (int32)
  - `nom` (string)
  - `email` (string)

- **Message `ClientRequest`** pour la requête :
  - `id` (int32)

- **Message `ClientResponse`** pour la réponse :
  - `client` (type Client, optionnel)
  - `error` (string, pour gérer les erreurs)

- **Service `ClientService`** avec une méthode RPC :
  - `GetClient(ClientRequest)` qui retourne `ClientResponse`

### Étape 2 : Générer les fichiers Python

Compilez le fichier `.proto` pour générer les fichiers Python nécessaires :

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. client.proto
```

ou 

Avec les scripts dans les dossier : `windows` et `linux`

Cela génère :
- `client_pb2.py` : Classes de messages
- `client_pb2_grpc.py` : Classes de services

### Étape 3 : Implémenter le Serveur

Dans `server.py`, implémentez :

1. Une classe `ClientServiceServicer` qui hérite de `client_pb2_grpc.ClientServiceServicer`
2. La méthode `GetClient` qui :
   - Vérifie que l'ID est valide (> 0)
   - Retourne une erreur si l'ID est invalide
   - Retourne un objet `Client` avec des données exemple si l'ID est valide
3. Une fonction `serve()` qui :
   - Crée un serveur gRPC
   - Enregistre le service
   - Écoute sur le port 50051
   - Attend les connexions

### Étape 4 : Implémenter le Client

Dans `client.py`, implémentez :

1. Une fonction `get_client(client_id)` qui :
   - Se connecte au serveur sur `localhost:50051`
   - Crée un stub pour appeler le service
   - Envoie une requête avec l'ID du client
   - Affiche le résultat ou l'erreur reçue

### Étape 5 : Écrire les Tests

Dans `client_test.py`, créez des tests unitaires qui vérifient :

1. La récupération d'un client avec un ID valide
2. La gestion d'erreur pour un ID invalide (négatif)

## Exécution

### Lancer le serveur

```bash
python server.py
```

Le serveur démarre et affiche :
```
Serveur gRPC démarré sur le port 50051
```

### Lancer le client

Dans un autre terminal :

```bash
python client.py
```

Résultat attendu :
```
Client récupéré: Dupont (dupont@example.com)
```

### Lancer les tests

```bash
python client_test.py
```

## Points Clés à Comprendre

1. **Protocol Buffers** : Langage de sérialisation de données structurées
2. **gRPC** : Framework RPC haute performance basé sur HTTP/2
3. **Stub** : Client-side proxy pour appeler les méthodes distantes
4. **Servicer** : Classe serveur qui implémente la logique métier
5. **Gestion des erreurs** : Utilisation de messages d'erreur dans les réponses

## Extensions Possibles

- Ajouter une base de données pour stocker les clients
- Implémenter d'autres méthodes CRUD (Create, Update, Delete)
- Ajouter l'authentification
- Utiliser le streaming gRPC pour des requêtes multiples
- Gérer les métadonnées et les intercepteurs

## Ressources

- [Documentation gRPC Python](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)

---

**Bon courage !**