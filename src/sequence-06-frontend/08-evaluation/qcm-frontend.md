# QCM Séquence 6 - Front-End gRPC-Web

**Durée**: 15 minutes  
**Questions**: 15  
**Note de passage**: 70% (11/15 correct)  
**Tentatives**: 2 maximum

---

## Question 1: Limitations des navigateurs

**Pourquoi ne peut-on pas utiliser gRPC natif directement dans un navigateur?**

A) Les navigateurs ne supportent pas HTTP/2  
B) Les navigateurs n'ont pas accès direct aux frames HTTP/2 nécessaires pour gRPC  
C) Protocol Buffers n'est pas supporté en JavaScript  
D) gRPC n'est compatible qu'avec les serveurs Node.js

**Réponse correcte**: B  
**Explication**: Les navigateurs supportent HTTP/2, mais n'exposent pas les APIs de bas niveau nécessaires pour manipuler directement les frames HTTP/2 comme le requiert gRPC natif.

---

## Question 2: Rôle d'Envoy

**Quel est le rôle principal du proxy Envoy dans une architecture gRPC-Web?**

A) Compiler les fichiers .proto en JavaScript  
B) Traduire les requêtes gRPC-Web du navigateur en gRPC natif pour le backend  
C) Remplacer React comme framework frontend  
D) Gérer la base de données

**Réponse correcte**: B  
**Explication**: Envoy agit comme un proxy qui traduit les requêtes gRPC-Web (compatibles navigateur) en gRPC natif (requis par le backend).

---

## Question 3: Streaming gRPC-Web

**Quel type de streaming est supporté par gRPC-Web?**

A) Streaming bidirectionnel uniquement  
B) Client streaming uniquement  
C) Server streaming uniquement  
D) Tous les types de streaming

**Réponse correcte**: C  
**Explication**: gRPC-Web supporte uniquement le server streaming. Le client streaming et le streaming bidirectionnel ne sont pas disponibles dans les navigateurs.

---

## Question 4: Content-Type

**Quel Content-Type est recommandé pour les requêtes gRPC-Web?**

A) application/json  
B) application/grpc  
C) application/grpc-web+proto  
D) text/plain

**Réponse correcte**: C  
**Explication**: `application/grpc-web+proto` indique une requête gRPC-Web avec sérialisation Protocol Buffers, c'est le format recommandé.

---

## Question 5: Configuration CORS

**Dans quelle configuration doit être placé le filtre CORS dans Envoy?**

A) Après le filtre gRPC-Web  
B) Avant le filtre gRPC-Web  
C) L'ordre n'a pas d'importance  
D) CORS n'est pas nécessaire pour gRPC-Web

**Réponse correcte**: B  
**Explication**: Le filtre CORS doit être placé AVANT le filtre gRPC-Web pour traiter correctement les preflight requests (OPTIONS).

---

## Question 6: Génération de stubs

**Quelle commande génère des stubs JavaScript à partir d'un fichier .proto?**

A) `npm install grpc-web`  
B) `protoc --js_out=. --grpc-web_out=. user.proto`  
C) `node generate-stubs.js`  
D) `grpc-compile user.proto`

**Réponse correcte**: B  
**Explication**: `protoc` avec les plugins `--js_out` et `--grpc-web_out` génère les stubs JavaScript/gRPC-Web.

---

## Question 7: Import des stubs

**Comment importer correctement le client gRPC-Web généré?**

A) `import client from 'grpc-web';`  
B) `import {UserServiceClient} from './proto/user_grpc_web_pb';`  
C) `const client = require('grpc');`  
D) `import * as grpc from '@grpc/grpc-js';`

**Réponse correcte**: B  
**Explication**: Les stubs générés doivent être importés depuis le fichier `*_grpc_web_pb` généré par protoc.

---

## Question 8: Création du client

**Comment créer une instance du client gRPC-Web?**

A) `new UserServiceClient()`  
B) `new UserServiceClient('http://localhost:8080')`  
C) `UserServiceClient.connect('localhost:8080')`  
D) `grpcWeb.createClient('localhost:8080')`

**Réponse correcte**: B  
**Explication**: Le client gRPC-Web est instancié avec l'URL du proxy Envoy (pas du backend gRPC).

---

## Question 9: Gestion des erreurs

**Comment vérifier si une requête gRPC-Web a échoué?**

A) Vérifier `response.status === 200`  
B) Vérifier `err != null` dans le callback  
C) Vérifier `response.success === true`  
D) Les erreurs sont impossibles avec gRPC-Web

**Réponse correcte**: B  
**Explication**: Les callbacks gRPC-Web suivent la convention Node.js: premier paramètre est l'erreur (null si succès).

---

## Question 10: Promesses vs Callbacks

**Quelle syntaxe est correcte pour utiliser des Promesses avec gRPC-Web?**

A) `client.getUser(request).then(...)`  
B) `await client.getUser(request)`  
C) `client.getUser(request, {}, (err, response) => {...})`  
D) Les deux A et C sont correctes

**Réponse correcte**: D  
**Explication**: gRPC-Web supporte à la fois les callbacks (C) et les promesses (A). Le style async/await (B) ne fonctionne pas directement sans wrapper.

---

## Question 11: Server Streaming

**Comment écouter les messages d'un stream serveur?**

```javascript
const stream = client.streamLogs(request);
```

A) `stream.on('data', (log) => {...})`  
B) `for await (const log of stream) {...}`  
C) `stream.getData((log) => {...})`  
D) `stream.subscribe((log) => {...})`

**Réponse correcte**: A  
**Explication**: Les streams gRPC-Web utilisent l'API EventEmitter avec `on('data', callback)`.

---

## Question 12: Metadata/Headers

**Comment envoyer un token d'authentification avec une requête gRPC-Web?**

```javascript
const metadata = {'authorization': 'Bearer ' + token};
client.getUser(request, metadata, callback);
```

A) Oui, c'est correct  
B) Non, utiliser `client.setToken(token)`  
C) Non, les metadata ne sont pas supportés  
D) Non, utiliser `request.setAuthorization(token)`

**Réponse correcte**: A  
**Explication**: Les metadata sont passés comme second argument (objet JavaScript simple).

---

## Question 13: Debugging

**Quel outil est le plus utile pour déboguer les requêtes gRPC-Web?**

A) Postman  
B) Chrome DevTools (Network tab)  
C) gRPC UI  
D) curl

**Réponse correcte**: B  
**Explication**: Chrome DevTools permet de voir les requêtes HTTP, headers, payload, et erreurs CORS pour gRPC-Web.

---

## Question 14: Configuration Envoy - Port

**Sur quel port Envoy écoute-t-il généralement pour gRPC-Web (dans nos exemples)?**

A) 50051  
B) 3000  
C) 8080  
D) 443

**Réponse correcte**: C  
**Explication**: Par convention, Envoy écoute sur 8080 pour gRPC-Web (le backend gRPC est sur 50051).

---

## Question 15: Production

**Quelle configuration est OBLIGATOIRE en production?**

A) Load balancing  
B) TLS/HTTPS  
C) Multiple replicas Envoy  
D) Health checks

**Réponse correcte**: B  
**Explication**: TLS/HTTPS est obligatoire en production pour la sécurité. Les autres sont recommandés mais pas obligatoires.

---

## Barème

- **15/15**: Excellent! Maîtrise parfaite ⭐⭐⭐⭐⭐
- **13-14/15**: Très bien! Quelques petits détails 📚
- **11-12/15**: Bien, note de passage ✅
- **9-10/15**: À revoir, relisez les guides 📖
- **< 9/15**: Reprenez la séquence depuis le début 🔄

---

## Répartition des questions par thème

- **Concepts gRPC-Web** (Questions 1, 2, 3): 3 questions
- **Configuration Envoy** (Questions 4, 5, 14, 15): 4 questions  
- **Génération et imports** (Questions 6, 7, 8): 3 questions
- **Code React/JS** (Questions 9, 10, 11, 12): 4 questions
- **Debugging** (Question 13): 1 question

---

**Conseil**: Si vous avez moins de 70%, relisez:
- Guide Envoy (Chapitres 1-5)
- Guide React gRPC-Web (Chapitres 1-4)
- Exemples 01, 03, 05
