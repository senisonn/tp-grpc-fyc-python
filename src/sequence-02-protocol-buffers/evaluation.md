# Évaluation - Chapitre 2 : Protocol Buffers

## Durée : 10 minutes

## Instructions

Ce QCM contient 15 questions à choix multiples. Pour chaque question, **une ou plusieurs réponses** peuvent être correctes. Lisez attentivement chaque question et cochez toutes les bonnes réponses.

**Barème :**
- Bonne réponse complète : 1 point
- Réponse incomplète ou partiellement fausse : 0 point
- Total : 15 points

---

## Questions

### 1. Quelle est la syntaxe correcte pour déclarer un fichier Protocol Buffers en proto3 ?

- [ ] A. `version = "proto3";`
- [ ] B. `syntax = "proto3";`
- [ ] C. `proto3;`
- [ ] D. `@proto3`

---

### 2. Quels sont les avantages de Protocol Buffers par rapport à JSON ? (Plusieurs réponses possibles)

- [ ] A. Taille de données plus compacte
- [ ] B. Lisibilité humaine directe
- [ ] C. Sérialisation/désérialisation plus rapide
- [ ] D. Type-safety avec génération de code
- [ ] E. Plus facile à déboguer

---

### 3. Dans Protocol Buffers, que représentent les numéros de champ (field numbers) ?

- [ ] A. L'ordre d'affichage des champs
- [ ] B. L'identifiant unique utilisé dans la sérialisation binaire
- [ ] C. La priorité du champ
- [ ] D. La taille du champ en bytes

---

### 4. Quelle est la plage de numéros de champ recommandée pour les champs fréquemment utilisés ?

- [ ] A. 1-5
- [ ] B. 1-15
- [ ] C. 1-100
- [ ] D. 16-2047

---

### 5. Peut-on modifier le numéro d'un champ après le déploiement d'un schéma ?

- [ ] A. Oui, sans problème
- [ ] B. Non, jamais
- [ ] C. Oui, mais seulement si on augmente le numéro
- [ ] D. Oui, mais il faut recompiler tous les clients

---

### 6. Quel type Protocol Buffers faut-il utiliser pour stocker un timestamp Unix ?

- [ ] A. `int32`
- [ ] B. `int64`
- [ ] C. `uint64`
- [ ] D. `string`

---

### 7. Quelle est la valeur par défaut d'un champ `string` non défini en proto3 ?

- [ ] A. `null`
- [ ] B. `""`  (chaîne vide)
- [ ] C. `"undefined"`
- [ ] D. Aucune valeur (le champ n'existe pas)

---

### 8. Comment déclare-t-on une liste de strings en Protocol Buffers ?

- [ ] A. `list<string> tags = 1;`
- [ ] B. `repeated string tags = 1;`
- [ ] C. `string[] tags = 1;`
- [ ] D. `array<string> tags = 1;`

---

### 9. Quels types peuvent être utilisés comme clés dans un champ `map` ? (Plusieurs réponses possibles)

- [ ] A. `string`
- [ ] B. `int32`
- [ ] C. `float`
- [ ] D. `double`
- [ ] E. `bool`
- [ ] F. `bytes`

---

### 10. Dans une énumération proto3, quelle doit être la valeur du premier élément ?

- [ ] A. 1
- [ ] B. 0
- [ ] C. -1
- [ ] D. N'importe quelle valeur

---

### 11. Quelle commande permet de compiler un fichier `.proto` en Python ?

- [ ] A. `protoc --python_out=. file.proto`
- [ ] B. `python -m grpc_tools.protoc --proto_path=. --python_out=. file.proto`
- [ ] C. `grpc compile file.proto`
- [ ] D. `protobuf --compile file.proto`

---

### 12. Quels fichiers sont générés lors de la compilation d'un fichier `.proto` contenant des services ?

- [ ] A. `file_pb2.py`
- [ ] B. `file_pb2_grpc.py`
- [ ] C. `file.py`
- [ ] D. `file_service.py`

---

### 13. Comment sérialiser un message Protocol Buffers en Python ?

- [ ] A. `message.serialize()`
- [ ] B. `message.SerializeToString()`
- [ ] C. `message.to_bytes()`
- [ ] D. `protobuf.serialize(message)`

---

### 14. Que signifie le mot-clé `reserved` dans un message Protocol Buffers ?

- [ ] A. Marque un champ comme obligatoire
- [ ] B. Réserve un numéro de champ pour éviter sa réutilisation
- [ ] C. Marque un champ comme privé
- [ ] D. Indique que le champ est réservé aux administrateurs

---

### 15. Quelle est la meilleure pratique pour supprimer un champ d'un message existant ?

- [ ] A. Simplement le supprimer du fichier .proto
- [ ] B. Le commenter avec `//`
- [ ] C. Utiliser `reserved` pour marquer le numéro comme réservé
- [ ] D. Changer son type en `deprecated`

---

## Réponses

<details>
<summary>Cliquez ici pour voir les réponses (à ne consulter qu'après avoir répondu !)</summary>

### Réponses correctes

1. **B** - `syntax = "proto3";` est la déclaration correcte
2. **A, C, D** - Protocol Buffers est compact, rapide et type-safe (mais pas lisible directement)
3. **B** - Les field numbers sont des identifiants dans la sérialisation binaire
4. **B** - 1-15 utilisent 1 byte d'encodage (optimal)
5. **B** - Jamais ! Cela casserait la compatibilité
6. **B** - `int64` pour les timestamps Unix (en secondes ou millisecondes)
7. **B** - Chaîne vide `""`
8. **B** - `repeated string tags = 1;`
9. **A, B, E** - string, int32, et bool peuvent être clés (pas float, double, bytes)
10. **B** - Doit être 0 en proto3
11. **B** - `python -m grpc_tools.protoc --proto_path=. --python_out=. file.proto`
12. **A, B** - `file_pb2.py` (messages) et `file_pb2_grpc.py` (services)
13. **B** - `message.SerializeToString()`
14. **B** - Réserve un numéro pour éviter la réutilisation
15. **C** - Toujours utiliser `reserved` pour les champs supprimés

### Barème de notation

- **13-15 points** : Excellente maîtrise ✅
- **10-12 points** : Bonne compréhension, quelques révisions nécessaires ⚠️
- **7-9 points** : Compréhension partielle, relire le cours 📚
- **0-6 points** : Révision complète recommandée 🔄

</details>

---

## Questions Bonus (optionnelles)

### B1. Quel est l'avantage d'utiliser `sint32` au lieu de `int32` ?

- [ ] A. Aucun avantage
- [ ] B. Plus efficace pour les nombres négatifs
- [ ] C. Utilise moins de mémoire
- [ ] D. Plus rapide à sérialiser

### B2. Que fait la méthode `ParseFromString()` ?

- [ ] A. Sérialise un message en string
- [ ] B. Désérialise des bytes en message
- [ ] C. Convertit un message en JSON
- [ ] D. Parse une string en entier

### B3. Dans un `oneof`, combien de champs peuvent être définis simultanément ?

- [ ] A. Aucun
- [ ] B. Un seul
- [ ] C. Plusieurs
- [ ] D. Tous

<details>
<summary>Réponses bonus</summary>

- B1: **B** - `sint32` utilise un encodage zigzag plus efficace pour les nombres négatifs
- B2: **B** - Désérialise des bytes en message Protocol Buffers
- B3: **B** - Un seul champ peut être défini dans un `oneof`

</details>

---

## Ressources pour réviser

Si vous avez des difficultés, consultez :
- [Documentation du cours](../../docs/sequences/sequence-02-protocol-buffers.md)
- [Exemples de code](./examples/)
- [Proto3 Language Guide](https://protobuf.dev/programming-guides/proto3/)

---

**Prochaine étape :** Une fois l'évaluation complétée, passez à la Séquence 03 - Modèles de Communication gRPC
