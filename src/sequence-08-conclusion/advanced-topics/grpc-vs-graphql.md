**Introduction**
Deux technologies modernes pour les APIs, mais des philosophies différentes.

**Tableau Comparatif**

| Aspect | gRPC | GraphQL |
|--------|------|---------|
| **Protocole** | HTTP/2, Binaire (Protobuf) | HTTP/1.1, Texte (JSON) |
| **Typage** | Fort (schema proto) | Fort (schema GraphQL) |
| **Requêtes** | Méthodes fixes | Queries flexibles |
| **Performance** | Excellent (binaire) | Bon (JSON) |
| **Streaming** | Bidirectionnel natif | Subscriptions (WebSocket) |
| **Caching** | Complexe | Simple (HTTP cache) |
| **Courbe apprentissage** | Moyenne | Moyenne-Haute |
| **Tooling** | Bon | Excellent |
| **Browser support** | Via gRPC-Web + proxy | Natif |
| **Use case** | Microservices, IoT, Mobile | APIs publiques, Dashboards |

**Quand utiliser gRPC?**
- ✅ Communication microservices interne
- ✅ Performance critique
- ✅ Streaming bidirectionnel
- ✅ Contrat strict (proto)
- ✅ Multiplateforme (polyglotte)
- ✅ IoT et ressources limitées

**Quand utiliser GraphQL?**
- ✅ API publique flexible
- ✅ Frontend complexes (éviter over-fetching)
- ✅ Agrégation de données multiples sources
- ✅ Rapid prototyping
- ✅ Mobile avec connexion variable
- ✅ Documentation auto-générée

**Hybride: Utiliser les deux**
```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ GraphQL (flexible)
┌──────▼──────┐
│  Gateway    │
│  GraphQL    │
└──────┬──────┘
       │ gRPC (performant)
┌──────▼──────────────┬──────────┐
│  Microservice A    │  Micro B  │
└────────────────────┴───────────┘
```

**Exemple d'architecture:**
- Frontend ↔ GraphQL Gateway
- GraphQL Gateway ↔ gRPC Microservices
- Microservices ↔ gRPC entre eux

**Ressources:**
- [gRPC official](https://grpc.io)
- [GraphQL official](https://graphql.org)
- [Comparaison détaillée](https://lien-externe.com)