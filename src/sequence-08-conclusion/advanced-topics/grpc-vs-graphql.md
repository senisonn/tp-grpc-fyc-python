# Comparaison gRPC et GraphQL

## Introduction

gRPC et GraphQL sont deux technologies modernes pour construire des APIs, mais avec des philosophies et cas d'usage différents. Ce document compare les deux approches pour vous aider à choisir la meilleure solution selon votre contexte.

## Tableau Comparatif Détaillé

| Aspect | gRPC | GraphQL |
|--------|------|---------|
| **Protocole** | HTTP/2, Binaire (Protobuf) | HTTP/1.1/2, Texte (JSON) |
| **Typage** | Fort (schema .proto) | Fort (schema GraphQL) |
| **Définition API** | Service RPC avec méthodes fixes | Queries/Mutations/Subscriptions flexibles |
| **Requêtes** | Méthodes prédéfinies | Queries dynamiques côté client |
| **Performance** | Excellent (binaire compact) | Bon (JSON verbeux) |
| **Taille payload** | Petit (~30% plus petit que JSON) | Moyen |
| **Streaming** | Bidirectionnel natif | Subscriptions (WebSocket) |
| **Caching** | Complexe (binaire) | Simple (HTTP cache standard) |
| **Browser support** | Via gRPC-Web + Envoy proxy | Natif |
| **Courbe apprentissage** | Moyenne | Moyenne-Haute |
| **Tooling** | Bon (BloomRPC, grpcurl) | Excellent (GraphiQL, Apollo) |
| **Over-fetching** | Oui (retourne toujours tout) | Non (client spécifie champs) |
| **Under-fetching** | Possible (appels multiples) | Évité (requête unique) |
| **Versioning** | Proto packages (v1, v2) | Schema evolution |
| **Use case principal** | Microservices, IoT, Mobile | APIs publiques, Dashboards complexes |

## Philosophies Différentes

### gRPC : Contract-First, RPC-Style

**Principe :** Le serveur définit un contrat strict (proto), le client l'utilise.
```protobuf
// Serveur définit les méthodes
service UserService {
rpc GetUser(GetUserRequest) returns (User) {}
rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {}
}message User {
string id = 1;
string name = 2;
string email = 3;
string phone = 4;
Address address = 5;
}
```

**Avantages :**
- Contrat clair et immuable
- Typage fort garanti
- Performance maximale
- Adapté aux systèmes distribués

**Inconvénients :**
- Le client reçoit TOUT (même champs non utilisés)
- Changements = nouvelle version du proto
- Moins flexible

### GraphQL : Client-First, Query-Style

**Principe :** Le client demande exactement ce dont il a besoin.
```graphql
Client définit ce qu'il veut
query GetUserProfile {
user(id: "123") {
name
email
# Pas de phone ni address si non nécessaires
}
}Ou requête plus large
query GetUserComplete {
user(id: "123") {
name
email
phone
address {
city
country
}
}
}
```

**Avantages :**
- Pas d'over-fetching (client optimise)
- Une requête = toutes les données
- Très flexible
- Documentation auto-générée

**Inconvénients :**
- Complexité côté serveur (resolvers)
- Requêtes complexes = problèmes de performance
- Caching plus difficile

## Quand Utiliser gRPC ?

### ✅ Cas d'Usage Idéaux

**1. Communication Microservices Interne**

Service A (Python) ──gRPC──> Service B (Go) ──gRPC──> Service C (Java)


- Performance critique
- Typage fort entre services
- Contrat bien défini

**2. IoT et Appareils Limités**
- Bandwidth limité → Protobuf compact
- CPU/Mémoire limités → Binaire efficace
- Connexions instables → Retry natif

**3. Applications Mobiles Natives**
- iOS/Android : gRPC natif
- Économie de batterie (payload petit)
- Latence faible

**4. Streaming Temps Réel**
```protobuf
// Bidirectional streaming parfait pour chat
service ChatService {
rpc Chat(stream Message) returns (stream Message) {}
}
```

**5. APIs Internes d'Entreprise**
- Contrat strict requis
- Plusieurs langages
- Performance > Flexibilité

### Exemple Concret : Système de Paiement
```protobuf
service PaymentService {
rpc ProcessPayment(PaymentRequest) returns (PaymentResponse) {}
rpc GetPaymentStatus(StatusRequest) returns (PaymentStatus) {}
rpc StreamTransactions(Empty) returns (stream Transaction) {}
}// Performance critique : paiements rapides
// Typage fort : éviter erreurs financières
// Streaming : monitoring temps réel
```

## Quand Utiliser GraphQL ?

### ✅ Cas d'Usage Idéaux

**1. API Publique pour Frontend Complexe**
```graphql
query Dashboard {
user {
profile { name, avatar }
stats { postsCount, followersCount }
recentPosts(limit: 5) { title, excerpt }
notifications(unreadOnly: true) { message, timestamp }
}
}
```

Une requête au lieu de 5 REST/gRPC calls


**2. Mobile App avec Connexion Variable**
- Client choisit données selon réseau
- 4G : requête complète
- 3G/2G : requête minimale

**3. Dashboards et Admin Panels**
```graphql
query AdminDashboard {
users(filter: {active: true}) { id, email }
orders(status: "pending") { id, total }
revenue(period: "today") { amount }
}
```

Tout en une requête


**4. Aggregation Multi-Sources**
```graphql
GraphQL server agrège plusieurs backends
query ProductDetails {
product(id: "123") {        # PostgreSQL
name
price
}
inventory(id: "123") {      # MongoDB
stock
warehouse
}
reviews(productId: "123") { # Elasticsearch
rating
comment
}
}
```

**5. Rapid Prototyping**
- Schéma évolue facilement
- Playground GraphiQL
- Itérations rapides

### Exemple Concret : E-commerce Frontend
```graphql