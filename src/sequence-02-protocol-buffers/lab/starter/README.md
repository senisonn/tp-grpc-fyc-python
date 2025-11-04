# 🧩 TP1 — Protocol Buffers et Sérialisation avec gRPC

## 🎯 Objectif du TP

Ce TP a pour but de découvrir et manipuler les fichiers `.proto` utilisés par **gRPC** pour définir des messages et des services.
À la fin du TP, tu seras capable de :
1. Créer un fichier `.proto` avec la syntaxe proto3
2. Le compiler avec `grpc_tools.protoc`
3. Utiliser les classes générées pour sérialiser et désérialiser des données en Python
4. Comprendre les avantages de Protocol Buffers par rapport à JSON

## ⏱️ Durée estimée

1 heure

---

## 🧰 Pré-requis

Avant de commencer, vérifie que tu disposes de :
- **Python 3.10+** installé et ajouté au PATH
- Les bibliothèques nécessaires :
  ```bash
  pip install grpcio grpcio-tools
  # Ou avec poetry
  poetry install
  ```
- Un éditeur de code (VS Code, PyCharm, etc.)
- Quelques notions de base en programmation orientée objet (Python)

## 📦 Structure du projet attendue

```
tp-protocol-buffers-et-serialisation/
│
├── user.proto              # Votre schéma Protocol Buffers
├── user_pb2.py            # Généré par protoc (messages)
├── user_pb2_grpc.py       # Généré par protoc (services)
├── test_serialization.py   # Votre script de test
└── README.md              # Ce fichier
```

---

## 🧱 Étape 1 – Création du fichier .proto

### 🎯 Objectif

Définir la structure des messages qui seront échangés dans les services gRPC.

### 📄 À faire

Créer un fichier nommé `user.proto` à la racine du projet.
Ce fichier doit définir :

1. **Un message `User`** avec les champs :
   - `id` (int32) - Identifiant unique de l'utilisateur
   - `name` (string) - Nom complet de l'utilisateur
   - `email` (string) - Adresse email

2. **Un message `UserIdRequest`** pour les requêtes :
   - `id` (int32) - L'identifiant de l'utilisateur à récupérer

3. **Un service `UserService`** avec une méthode :
   - `GetUserById` qui prend un `UserIdRequest` et retourne un `User`

### 💡 Indications

- Le mot-clé `syntax = "proto3";` doit apparaître au début du fichier
- Les numéros de champ (= 1, = 2, …) identifient chaque donnée dans le flux binaire
- **IMPORTANT:** Ne changez JAMAIS ces numéros une fois le schéma déployé
- Les champs fréquemment utilisés devraient avoir les numéros 1-15 (encodage sur 1 byte)

### 📝 Structure attendue

```proto
syntax = "proto3";

// Définissez vos messages ici
message User {
  // Vos champs ici
}

message UserIdRequest {
  // Votre champ ici
}

// Définissez votre service ici
service UserService {
  // Votre méthode ici
}
```

### ✅ Critères de validation

- [ ] Le fichier commence par `syntax = "proto3";`
- [ ] Le message `User` contient 3 champs avec les bons types
- [ ] Chaque champ a un numéro unique
- [ ] Le service `UserService` est défini
- [ ] La méthode `GetUserById` est correctement typée

---

## ⚙️ Étape 2 – Compilation du fichier .proto

### 🎯 Objectif

Compiler le fichier `.proto` pour générer automatiquement le code Python correspondant.

### 📄 À faire

#### Sur Windows/Mac/Linux :

```bash
python -m grpc_tools.protoc \
  --proto_path=. \
  --python_out=. \
  --grpc_python_out=. \
  user.proto
```

**Explication des options:**
- `--proto_path=.` : Dossier où chercher les fichiers .proto
- `--python_out=.` : Dossier de sortie pour les messages
- `--grpc_python_out=.` : Dossier de sortie pour les services

### ✅ Résultat attendu

Deux fichiers générés à la racine du projet :
- `user_pb2.py` - Contient les classes Python pour vos messages
- `user_pb2_grpc.py` - Contient les stubs client/serveur pour vos services

### ⚠️ Erreurs courantes

**Erreur : `protoc: command not found`**
- Utilisez `python -m grpc_tools.protoc` au lieu de `protoc`

**Erreur : `File not found`**
- Vérifiez que vous êtes dans le bon dossier
- Vérifiez le nom du fichier (sensible à la casse)

**Erreur : `Syntax error`**
- Vérifiez que vous avez `syntax = "proto3";` au début
- Vérifiez les points-virgules à la fin de chaque ligne

---

## 🧪 Étape 3 – Tester la sérialisation et la désérialisation

### 🎯 Objectif

Vérifier que le message `User` peut être converti (sérialisé) en flux binaire puis reconverti (désérialisé) en objet Python.

### 📄 À faire

Créer un fichier `test_serialization.py` à la racine du projet.
Ce script doit :

1. Importer la classe `User` depuis `user_pb2`
2. Créer un objet `User` avec des données
3. Sérialiser cet objet avec `SerializeToString()`
4. Afficher la taille en bytes
5. Créer un nouvel objet `User`
6. Désérialiser les données avec `ParseFromString()`
7. Afficher les résultats pour vérifier

### 📝 Code de départ

```python
# Import des classes générées
from user_pb2 import User

# Étape 1 : Créer un utilisateur
print("=== Création de l'utilisateur ===")
user = User()
user.id = 1
user.name = "Alice Dupont"
user.email = "alice@example.com"

print(f"User créé : {user}")

# Étape 2 : Sérialisation
print("\n=== Sérialisation ===")
serialized_data = user.SerializeToString()
print(f"Données sérialisées : {serialized_data}")
print(f"Taille : {len(serialized_data)} bytes")

# Étape 3 : Désérialisation
print("\n=== Désérialisation ===")
user2 = User()
user2.ParseFromString(serialized_data)
print(f"User désérialisé : {user2}")
print(f"Nom : {user2.name}")
print(f"Email : {user2.email}")

# Étape 4 : Vérification
print("\n=== Vérification ===")
if user.name == user2.name and user.email == user2.email:
    print("✅ Sérialisation/Désérialisation réussie!")
else:
    print("❌ Erreur dans la sérialisation/désérialisation")
```

### ▶️ Commande à exécuter

```bash
python test_serialization.py
```

### ✅ Résultat attendu

```
=== Création de l'utilisateur ===
User créé : id: 1
name: "Alice Dupont"
email: "alice@example.com"

=== Sérialisation ===
Données sérialisées : b'\x08\x01\x12\x0cAlice Dupont\x1a\x12alice@example.com'
Taille : 31 bytes

=== Désérialisation ===
User désérialisé : id: 1
name: "Alice Dupont"
email: "alice@example.com"
Nom : Alice Dupont
Email : alice@example.com

=== Vérification ===
✅ Sérialisation/Désérialisation réussie!
```

---

## 🎓 Étape 4 – Comparaison avec JSON (optionnel)

### 🎯 Objectif

Comprendre les avantages de Protocol Buffers par rapport à JSON.

### 📄 À faire

Ajouter ce code à votre `test_serialization.py` :

```python
import json

print("\n=== Comparaison avec JSON ===")

# Sérialisation JSON
user_dict = {
    "id": 1,
    "name": "Alice Dupont",
    "email": "alice@example.com"
}
json_data = json.dumps(user_dict).encode('utf-8')
print(f"Taille JSON : {len(json_data)} bytes")
print(f"Taille Protocol Buffers : {len(serialized_data)} bytes")
print(f"Réduction : {((len(json_data) - len(serialized_data)) / len(json_data) * 100):.1f}%")
```

### 💡 Observations

Vous devriez observer que :
- Protocol Buffers est plus compact que JSON
- Les données binaires sont moins lisibles (mais plus efficaces)
- Protocol Buffers est typé (plus sûr)

---

## 🏆 Challenges Bonus

Si vous avez terminé le TP, essayez ces challenges :

### Challenge 1 : Ajouter des champs

Modifiez `user.proto` pour ajouter :
- Un champ `age` (int32)
- Un champ `is_active` (bool)
- Un champ `created_at` (int64) pour le timestamp

**N'oubliez pas de recompiler !**

### Challenge 2 : Utiliser des énumérations

Ajoutez un enum `Role` :
```proto
enum Role {
  ROLE_UNSPECIFIED = 0;
  ROLE_USER = 1;
  ROLE_ADMIN = 2;
  ROLE_MODERATOR = 3;
}
```

Ajoutez un champ `role` de type `Role` au message `User`.

### Challenge 3 : Collections

Ajoutez un champ `tags` de type `repeated string` au message `User` pour stocker une liste de tags.

Testez avec :
```python
user.tags.extend(["python", "grpc", "developer"])
```

### Challenge 4 : Benchmark de performance

Créez un benchmark qui :
1. Crée 10000 users
2. Mesure le temps de sérialisation en Protocol Buffers
3. Mesure le temps de sérialisation en JSON
4. Compare les résultats

---

## 📚 Ressources complémentaires

- [Documentation officielle Protocol Buffers](https://protobuf.dev/)
- [Guide Python Protocol Buffers](https://protobuf.dev/getting-started/pythontutorial/)
- [gRPC Python Quick Start](https://grpc.io/docs/languages/python/quickstart/)
- [Proto3 Language Guide](https://protobuf.dev/programming-guides/proto3/)

---

## ❓ FAQ

**Q: Puis-je modifier les numéros de champ ?**
R: NON ! Les numéros de champ sont utilisés dans le format binaire. Les changer casserait la compatibilité.

**Q: Que faire si je veux supprimer un champ ?**
R: Utilisez le mot-clé `reserved` pour marquer le numéro comme réservé :
```proto
message User {
  reserved 4, 5;  // Anciens champs supprimés
  int32 id = 1;
  // ...
}
```

**Q: Puis-je utiliser des types Python comme datetime ?**
R: Non directement. Utilisez `google.protobuf.Timestamp` ou un `int64` pour les timestamps.

**Q: Protocol Buffers est-il lisible par l'humain ?**
R: Non, c'est un format binaire. Pour le debugging, utilisez `MessageToJson()` de `google.protobuf.json_format`.

---

## ✅ Checklist finale

Avant de passer à la suite, vérifiez que :

- [ ] Vous avez créé un fichier `user.proto` valide
- [ ] La compilation génère `user_pb2.py` et `user_pb2_grpc.py` sans erreur
- [ ] Votre script `test_serialization.py` fonctionne correctement
- [ ] Vous comprenez la différence entre sérialisation et désérialisation
- [ ] Vous comprenez l'importance des numéros de champ
- [ ] Vous avez comparé Protocol Buffers avec JSON
- [ ] Vous avez essayé au moins un challenge bonus

---

## 📝 Pour aller plus loin

Consultez la solution complète dans le dossier `../solution/` si vous êtes bloqué.

**Prochaine étape :** Séquence 03 - Modèles de communication gRPC


