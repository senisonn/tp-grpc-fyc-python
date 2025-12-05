# QCM : Implémentation Back-End gRPC Python

**15 questions - 15 points - 30 minutes**

---

## Thème 1 : Setup et Configuration (3 questions)

### Question 1
Quelles dépendances Python sont nécessaires pour créer un serveur gRPC?

A) requests, flask  
B) grpcio, grpcio-tools, protobuf  
C) django, sqlalchemy  
D) fastapi, uvicorn  

**Réponse correcte : B**

---

### Question 2
Quelle commande génère les stubs Python depuis un fichier `user.proto`?

A) `protoc user.proto --python_out=.`  
B) `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto`  
C) `grpc compile user.proto`  
D) `pip install user.proto`  

**Réponse correcte : B**

---

### Question 3
Quel port est conventionnellement utilisé pour gRPC?

A) 8080  
B) 3000  
C) 50051  
D) 443  

**Réponse correcte : C**

---

## Thème 2 : Service CRUD (4 questions)

### Question 4
Comment implémenter la méthode CreateUser dans un servicer gRPC?

A) Créer une classe héritant de `UserServiceServicer` et implémenter la méthode  
B) Utiliser un décorateur `@grpc.method`  
C) Enregistrer une fonction callback  
D) Créer un endpoint HTTP  

**Réponse correcte : A**

---

### Question 5
Comment implémenter la pagination dans ListUsers?

A) Utiliser `page` et `page_size` dans la requête, calculer offset et limit  
B) Tout retourner, le client pagine  
C) Utiliser SQL LIMIT sans OFFSET  
D) La pagination n'est pas possible en gRPC  

**Réponse correcte : A**

---

### Question 6
Quelle est la bonne façon de retourner un utilisateur dans GetUser?

A) `return {"id": "123", "name": "John"}`  
B) `return user_pb2.User(id="123", name="John")`  
C) `return json.dumps(user)`  
D) `context.send(user)`  

**Réponse correcte : B**

---

### Question 7
Comment implémenter DeleteUser?

A) Retourner un booléen directement  
B) Retourner un message DeleteUserResponse avec success et message  
C) Retourner un objet User vide  
D) Ne rien retourner  

**Réponse correcte : B**

---

## Thème 3 : Gestion des Erreurs (4 questions)

### Question 8
Quel code de statut gRPC utiliser si un utilisateur n'existe pas?

A) INTERNAL  
B) INVALID_ARGUMENT  
C) NOT_FOUND  
D) UNAVAILABLE  

**Réponse correcte : C**

---

### Question 9
Comment signaler une erreur dans un servicer gRPC?

A) `raise Exception("Error")`  
B) `return None`  
C) `context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Error message")`  
D) `print("Error")`  

**Réponse correcte : C**

---

### Question 10
Quel code de statut pour des arguments invalides (email mal formaté)?

A) NOT_FOUND  
B) INVALID_ARGUMENT  
C) PERMISSION_DENIED  
D) INTERNAL  

**Réponse correcte : B**

---

### Question 11
Quelle est la différence entre INTERNAL et UNAVAILABLE?

A) Aucune différence  
B) INTERNAL = erreur serveur, UNAVAILABLE = service temporairement indisponible  
C) INTERNAL = erreur client, UNAVAILABLE = erreur serveur  
D) UNAVAILABLE n'existe pas  

**Réponse correcte : B**

---

## Thème 4 : Intercepteurs (3 questions)

### Question 12
À quoi sert un intercepteur gRPC?

A) Intercepter les requêtes HTTP  
B) Exécuter du code avant/après chaque appel RPC  
C) Bloquer toutes les requêtes  
D) Compiler les fichiers proto  

**Réponse correcte : B**

---

### Question 13
Dans quel ordre les intercepteurs s'exécutent-ils?

A) Ordre aléatoire  
B) Ordre inverse de déclaration  
C) Ordre de déclaration (premier déclaré = premier exécuté)  
D) Ordre alphabétique  

**Réponse correcte : C**

---

### Question 14
Comment implémenter un intercepteur de logging?

A) Hériter de `grpc.ServerInterceptor` et implémenter `intercept_service`  
B) Utiliser le décorateur `@log`  
C) Configurer logging.basicConfig  
D) Créer un middleware HTTP  

**Réponse correcte : A**

---

## Thème 5 : Tests (1 question)

### Question 15
Comment tester un service gRPC avec pytest?

A) Créer un serveur de test, instancier le service, appeler les méthodes  
B) Tests impossibles avec gRPC  
C) Utiliser curl  
D) Tester uniquement avec Postman  

**Réponse correcte : A**

---

## Barème

- 15 questions × 1 point = 15 points
- Note de passage : 60% (9/15)
- Durée : 30 minutes
- 2 tentatives autorisées

---

## Réponses (pour le formateur)

1. B
2. B
3. C
4. A
5. A
6. B
7. B
8. C
9. C
10. B
11. B
12. B
13. C
14. A
15. A
