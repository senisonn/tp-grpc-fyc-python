# 🧩 TP1 — Protocol Buffers et Sérialisation avec gRPC

## 🎯 Objectif du TP

Ce TP a pour but de découvrir et manipuler les fichiers `.proto` utilisés par **gRPC** pour définir des messages et des services.  
À la fin du TP, tu seras capable de :
1. Créer un fichier `.proto`
2. Le compiler avec `grpc_tools.protoc`
3. Utiliser les classes générées pour sérialiser et désérialiser des données en Python

---

## 🧰 Pré-requis

Avant de commencer, vérifie que tu disposes de :
- **Python 3.10+** installé et ajouté au PATH  
- Les bibliothèques nécessaires :
  ```bash
  pip install grpcio grpcio-tools
  
Un éditeur de code (VS Code, PyCharm, etc.)

Quelques notions de base en programmation orientée objet (Python)

## 📦 Structure du projet attendue

  tp-protocol-buffers-et-serialisation/
  │
  ├── user.proto
  ├── user_pb2.py
  ├── user_pb2_grpc.py
  ├── test_serialization.py
  ├── windows/
  │   └── compile_proto.bat
  └── README.md


## 🧱 Étape 1 – Création du fichier .proto
  🎯 Objectif
  
  Définir la structure des messages qui seront échangés dans les services gRPC.
  
  📄 À faire
    
    Créer un fichier nommé user.proto à la racine du projet.
    Ce fichier doit définir :
    
    Un message User avec les champs :
    
      id (int32)
      
      name (string)
      
      email (string)
    
    Un message UserIdRequest pour les requêtes d’un utilisateur par son identifiant
    
    Un service UserService avec une méthode GetUserById
  
  💡 Indications
  
    Le mot-clé syntax = "proto3"; doit apparaître au début du fichier.
    Les numéros de champ (= 1, = 2, …) identifient chaque donnée dans le flux binaire.
    
    ⚙️ Étape 2 – Compilation du fichier .proto
    🎯 Objectif
    
    Compiler le fichier .proto pour générer automatiquement le code Python correspondant.
    
    📄 À faire
    
    Utiliser le script fourni sous Windows :
    
      .\windows\compile_proto.bat

## ✅ Résultat attendu

  Deux fichiers générés à la racine du projet :
    user_pb2.py
    user_pb2_grpc.py

## 🧪 Étape 3 – Tester la sérialisation et la désérialisation
  🎯 Objectif
  
    Vérifier que le message User peut être converti (sérialisé) en flux binaire puis reconverti (désérialisé) en objet Python.
  
  📄 À faire
    
    Créer un fichier test_serialization.py à la racine du projet.
    Ce script doit :
    
      Importer la classe User depuis user_pb2
      
      Créer un objet User
      
      Sérialiser cet objet avec SerializeToString()
      
      Désérialiser les données avec ParseFromString()
      
      Afficher les résultats à l’écran
    
  ▶️ Commande à exécuter

    python test_serialization.py



