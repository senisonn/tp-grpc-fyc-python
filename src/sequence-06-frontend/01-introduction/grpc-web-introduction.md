# Introduction à gRPC-Web

## 🌐 Pourquoi gRPC-Web?

### Le problème: gRPC et les navigateurs

gRPC utilise HTTP/2 et nécessite un accès direct aux frames HTTP/2, ce qui n'est **pas possible depuis un navigateur web** pour plusieurs raisons:

#### Limitations des navigateurs

1. **Pas d'accès direct à HTTP/2**
   - Les navigateurs n'exposent pas les APIs HTTP/2 de bas niveau
   - Impossible de contrôler les frames HTTP/2 directement
   - Le standard gRPC nécessite des fonctionnalités HTTP/2 spécifiques

2. **Restrictions de sécurité**
   - Same-Origin Policy (SOP)
   - CORS (Cross-Origin Resource Sharing) requis
   - Limitations sur les headers personnalisés

3. **APIs limitées**
   - Fetch API et XMLHttpRequest ne supportent pas toutes les features gRPC
   - Pas de support natif pour les trailers HTTP/2
   - Streaming binaire limité

### La solution: gRPC-Web

gRPC-Web est un protocole qui permet aux applications web (JavaScript dans le navigateur) de communiquer avec des services gRPC backend.

**Comment ça fonctionne?**
```
[Navigateur]  →  gRPC-Web/HTTP  →  [Proxy]  →  gRPC/HTTP2  →  [Backend]
  (Client)         (Request)        (Envoy)     (Standard)      (Service)
```

## 🏗️ Architecture gRPC-Web

### Composants

```
┌─────────────────┐
│   Application   │
│      React      │  ← Code métier de votre frontend
└────────┬────────┘
         │
         │ Utilise
         ▼
┌─────────────────┐
│  Client         │
│  gRPC-Web       │  ← Stubs générés depuis .proto
└────────┬────────┘
         │
         │ HTTP/1.1 ou HTTP/2
         │ (selon navigateur)
         ▼
┌─────────────────┐
│  Envoy Proxy    │  ← Traduction gRPC-Web ↔ gRPC
│  (ou autre)     │     + CORS + Routing
└────────┬────────┘
         │
         │ gRPC pur (HTTP/2)
         ▼
┌─────────────────┐
│   Services      │
│   gRPC Back     │  ← Vos services Python/Go/Java...
└─────────────────┘
```

### Rôle du Proxy (Envoy)

Le proxy est **essentiel** car il:

1. **Traduit les protocoles**
   ```
   gRPC-Web (navigateur) ↔ gRPC natif (backend)
   ```

2. **Gère CORS**
   - Ajoute les headers CORS nécessaires
   - Gère les preflight requests (OPTIONS)

3. **Route les requêtes**
   - Peut router vers différents services backend
   - Load balancing
   - Retry logic

4. **Ajoute de la sécurité**
   - TLS termination
   - Authentification
   - Rate limiting

## 📊 Comparaison gRPC vs gRPC-Web

| Fonctionnalité | gRPC (natif) | gRPC-Web |
|----------------|--------------|----------|
| **Protocole de transport** | HTTP/2 uniquement | HTTP/1.1 ou HTTP/2 |
| **Environnement** | Serveur-à-serveur | Navigateur-vers-serveur |
| **Streaming** | ✅ Bidirectionnel complet | ⚠️ Serveur uniquement |
| **Performance** | ⭐⭐⭐⭐⭐ Optimale | ⭐⭐⭐⭐ Très bonne |
| **Headers/Trailers** | ✅ Support complet | ⚠️ Support partiel |
| **Proxy nécessaire** | ❌ Non | ✅ Oui (Envoy) |
| **Langages** | Tous | JavaScript/TypeScript |

### Limitations de gRPC-Web

1. **Pas de streaming client**
   ```javascript
   // ❌ NE FONCTIONNE PAS
   const stream = client.uploadFiles();
   stream.write(chunk1);
   stream.write(chunk2);
   ```
   
   **Solution**: Envoyer des requêtes unaires multiples ou utiliser server streaming

2. **Pas de streaming bidirectionnel**
   ```javascript
   // ❌ NE FONCTIONNE PAS
   const stream = client.chat();
   stream.on('data', handleMessage);
   stream.write(message);
   ```
   
   **Solution**: Utiliser server streaming + polling ou WebSockets pour vrai bidirectionnel

3. **Overhead du proxy**
   - Latence additionnelle (généralement <5ms)
   - Point de défaillance supplémentaire

## 🎯 Cas d'usage gRPC-Web

### ✅ Idéal pour:

1. **Applications Web Modernes**
   ```javascript
   // Dashboard en temps réel
   const stream = client.streamMetrics(request);
   stream.on('data', (metrics) => {
     updateDashboard(metrics);
   });
   ```

2. **APIs typées fortement**
   ```typescript
   // Autocomplétion et type safety
   const request = new GetUserRequest();
   request.setUserId(123);
   
   const response = await client.getUser(request);
   const user: User = response.getUser(); // Typé!
   ```

3. **Performance critique**
   - Sérialisation Protocol Buffers (plus rapide que JSON)
   - Compression automatique
   - Multiplexing HTTP/2

4. **Microservices Web**
   ```
   Frontend React → gRPC-Web → Envoy → Microservices
   ```

### ⚠️ À éviter si:

1. **Besoin de streaming bidirectionnel** → Utiliser WebSockets
2. **Support navigateurs anciens** (< IE11) → Utiliser REST
3. **Pas de contrôle sur l'infra** (pas de proxy) → REST/GraphQL
4. **API publique grand public** → REST est plus universel

## 🔄 Flux d'une requête gRPC-Web

### Requête Unaire

```
1. Client JavaScript
   const request = new GetUserRequest();
   request.setUserId(123);
   
2. Sérialisation (Protocol Buffers)
   request → bytes binaires
   
3. HTTP POST vers Envoy
   POST /user.UserService/GetUser
   Content-Type: application/grpc-web+proto
   Body: <binary protobuf>
   
4. Envoy traduit vers gRPC natif
   → HTTP/2 frames vers backend
   
5. Backend traite
   → Retourne User protobuf
   
6. Envoy traduit la réponse
   → gRPC-Web response
   
7. Client désérialise
   bytes → User object
   
8. Application utilise
   const name = response.getUser().getName();
```

### Server Streaming

```
1. Client ouvre le stream
   const stream = client.streamLogs(request);
   
2. Envoy maintient la connexion
   → Long-lived HTTP connection
   
3. Backend envoie des messages
   → Multiple protobuf messages
   
4. Client reçoit progressivement
   stream.on('data', (log) => {
     console.log(log.getMessage());
   });
   
5. Fin du stream
   stream.on('end', () => {
     console.log('Stream terminé');
   });
```

## 🛠️ Outils et Ecosystem

### 1. Protocole Buffers
```protobuf
// user.proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc StreamUsers(StreamUsersRequest) returns (stream User);
}

message GetUserRequest {
  int64 user_id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
}
```

### 2. Génération de code
```bash
# Génère les stubs JavaScript
protoc -I=. user.proto \
  --js_out=import_style=commonjs:./generated \
  --grpc-web_out=import_style=commonjs,mode=grpcwebtext:./generated
```

### 3. Client JavaScript
```javascript
import {UserServiceClient} from './generated/user_grpc_web_pb';
import {GetUserRequest} from './generated/user_pb';

const client = new UserServiceClient('http://localhost:8080');

const request = new GetUserRequest();
request.setUserId(123);

client.getUser(request, {}, (err, response) => {
  if (err) {
    console.error(err);
  } else {
    console.log(response.getUser().toObject());
  }
});
```

### 4. Proxies supportés

| Proxy | Support | Production Ready | Popularité |
|-------|---------|------------------|------------|
| **Envoy** | ⭐⭐⭐⭐⭐ Excellent | ✅ Oui | ⭐⭐⭐⭐⭐ |
| **Nginx** | ⭐⭐⭐ Bon | ✅ Oui | ⭐⭐⭐⭐ |
| **Traefik** | ⭐⭐⭐ Bon | ✅ Oui | ⭐⭐⭐ |
| **grpcwebproxy** | ⭐⭐ Basique | ⚠️ Dev only | ⭐⭐ |

**Recommandation**: Envoy (utilisé dans ce cours)

## 📈 Avantages de gRPC-Web

### 1. Performance
- Protocol Buffers: 3-10x plus compact que JSON
- Parsing plus rapide
- Compression native

### 2. Type Safety
```typescript
// Avec gRPC-Web + TypeScript
const user = response.getUser();
user.getName();  // ✅ Autocomplétion
user.getAgee(); // ❌ Erreur de compilation

// Avec REST/JSON
const user = response.user;
user.name;  // ✅ Pas de vérification
user.namee; // ❌ Erreur à l'exécution seulement
```

### 3. Schema-First Development
- Le fichier `.proto` est la source de vérité
- Backend et frontend partagent le même contrat
- Génération automatique de code

### 4. Streaming
```javascript
// Données en temps réel
const stream = client.streamStockPrices(request);
stream.on('data', (price) => {
  updateChart(price.getValue());
});
```

### 5. Rétrocompatibilité
- Ajout de champs sans casser les clients
- Versioning simplifié

## 🚀 Prochaines étapes

Maintenant que vous comprenez **pourquoi** et **comment** gRPC-Web fonctionne, nous allons apprendre à:

1. **Configurer Envoy Proxy** (Activité 2)
   - Installation
   - Configuration CORS
   - Routage

2. **Générer les stubs JavaScript** (Activité 3)
   - Compiler les .proto
   - Intégrer dans votre projet

3. **Implémenter un client React** (Activités 4-5)
   - Créer des clients gRPC
   - Gérer les états
   - Patterns avancés

4. **Déboguer** (Activité 6)
   - DevTools
   - Logs Envoy
   - Problèmes courants

## 📚 Ressources complémentaires

### Documentation officielle
- [gRPC-Web GitHub](https://github.com/grpc/grpc-web)
- [Envoy gRPC-Web filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_web_filter)

### Tutoriels
- [gRPC-Web Hello World](https://github.com/grpc/grpc-web/tree/master/net/grpc/gateway/examples/helloworld)
- [Building gRPC-Web Apps](https://grpc.io/docs/platforms/web/basics/)

### Articles
- [gRPC-Web is Going GA](https://grpc.io/blog/grpc-web-ga/)
- [Why gRPC-Web?](https://grpc.io/blog/state-of-grpc-web/)

## ✅ Vérification de compréhension

Avant de continuer, assurez-vous de pouvoir répondre à ces questions:

1. Pourquoi ne peut-on pas utiliser gRPC natif dans un navigateur?
2. Quel est le rôle du proxy Envoy?
3. Quelle est la principale limitation de gRPC-Web vs gRPC natif?
4. Quand devrait-on utiliser gRPC-Web vs REST?
5. Quels sont les 3 composants principaux d'une architecture gRPC-Web?

**Réponses** dans le guide PDF "Envoy Proxy" (section Introduction).

---

**Prochaine étape**: Configuration d'Envoy Proxy →  
**Durée estimée**: 40 minutes

*Questions? Postez sur le forum!*
