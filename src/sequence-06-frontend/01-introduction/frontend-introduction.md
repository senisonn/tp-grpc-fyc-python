# Introduction au Client Frontend gRPC-Web

## Architecture Client-Serveur gRPC-Web

### Le Défi HTTP/2

gRPC natif utilise HTTP/2, non supporté directement par les navigateurs. Solution: **gRPC-Web**

```
┌──────────────┐      gRPC-Web (HTTP/1.1)      ┌─────────────┐
│   Browser    │────────────────────────────────>│   Proxy     │
│   (React)    │                                 │  (Envoy)    │
└──────────────┘                                 └──────┬──────┘
                                                        │
                                                  gRPC (HTTP/2)
                                                        │
                                                        ▼
                                                 ┌─────────────┐
                                                 │   Backend   │
                                                 │   Server    │
                                                 └─────────────┘
```

## Stack Technologique

**Frontend:**
- React 18+
- grpc-web
- @improbable-eng/grpc-web
- TypeScript (optionnel)

**Build:**
- Vite ou Create React App
- Protobuf compiler
- protoc-gen-grpc-web

**Proxy:**
- Envoy (recommandé)
- grpc-web proxy

## Structure Projet React

```
react-grpc-client/
├── public/
│   └── index.html
├── src/
│   ├── proto/                    # Fichiers .proto
│   │   └── user.proto
│   ├── generated/                # Stubs générés
│   │   ├── user_pb.js
│   │   └── user_grpc_web_pb.js
│   ├── services/                 # Clients gRPC
│   │   └── userClient.js
│   ├── components/               # Composants React
│   │   ├── UserList.jsx
│   │   ├── UserForm.jsx
│   │   └── UserDetail.jsx
│   ├── hooks/                    # Custom hooks
│   │   └── useGrpcClient.js
│   ├── utils/                    # Utilitaires
│   │   └── errorHandler.js
│   ├── App.jsx
│   └── index.jsx
├── package.json
├── vite.config.js
└── README.md
```

## Client gRPC-Web vs REST

| Aspect | gRPC-Web | REST |
|--------|----------|------|
| Format | Protobuf (binaire) | JSON (texte) |
| Typage | Fort (proto) | Faible |
| Performance | Excellent | Bon |
| Streaming | Oui (server-side) | Non standard |
| Outils | protoc | Swagger/OpenAPI |
| Taille payload | Petit | Plus grand |

## Exemple Minimal

```javascript
// services/userClient.js
import { UserServiceClient } from '../generated/user_grpc_web_pb';
import { GetUserRequest } from '../generated/user_pb';

const client = new UserServiceClient('http://localhost:8080');

export function getUser(userId) {
  const request = new GetUserRequest();
  request.setUserId(userId);
  
  return new Promise((resolve, reject) => {
    client.getUser(request, {}, (err, response) => {
      if (err) {
        reject(err);
      } else {
        resolve(response.toObject());
      }
    });
  });
}
```

```jsx
// components/UserProfile.jsx
import React, { useEffect, useState } from 'react';
import { getUser } from '../services/userClient';

export default function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    getUser(userId)
      .then(setUser)
      .catch(setError);
  }, [userId]);
  
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

## Configuration Proxy Envoy

```yaml
# envoy.yaml
static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8080
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          codec_type: auto
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: local_service
              domains: ["*"]
              routes:
              - match:
                  prefix: "/"
                route:
                  cluster: grpc_backend
                  timeout: 0s
                  max_stream_duration:
                    grpc_timeout_header_max: 0s
              cors:
                allow_origin_string_match:
                - prefix: "*"
                allow_methods: GET, PUT, DELETE, POST, OPTIONS
                allow_headers: keep-alive,user-agent,cache-control,content-type,content-transfer-encoding,custom-header-1,x-accept-content-transfer-encoding,x-accept-response-streaming,x-user-agent,x-grpc-web,grpc-timeout
                max_age: "1728000"
                expose_headers: custom-header-1,grpc-status,grpc-message
          http_filters:
          - name: envoy.filters.http.grpc_web
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
          - name: envoy.filters.http.cors
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
  clusters:
  - name: grpc_backend
    connect_timeout: 0.25s
    type: logical_dns
    http2_protocol_options: {}
    lb_policy: round_robin
    load_assignment:
      cluster_name: grpc_backend
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: localhost
                port_value: 50051
```

## Patterns React + gRPC

### 1. Custom Hook Pattern

```javascript
function useUserData(userId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    setLoading(true);
    getUser(userId)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [userId]);
  
  return { data, loading, error };
}
```

### 2. Context Pattern

```javascript
const GrpcContext = createContext();

export function GrpcProvider({ children }) {
  const client = new UserServiceClient('http://localhost:8080');
  return (
    <GrpcContext.Provider value={client}>
      {children}
    </GrpcContext.Provider>
  );
}

export function useGrpcClient() {
  return useContext(GrpcContext);
}
```

### 3. Error Boundary Pattern

```jsx
class GrpcErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

## Gestion d'État

**Options:**
1. useState/useEffect (simple)
2. useReducer (complexe)
3. Context API (global)
4. Redux Toolkit (très complexe)
5. React Query (recommandé pour gRPC)

## Bonnes Pratiques

✅ **À faire:**
- Gérer les erreurs réseau
- Afficher des états de chargement
- Implémenter retry logic
- Valider côté client
- Utiliser TypeScript pour typage
- Centraliser la configuration client
- Logger les erreurs gRPC

❌ **À éviter:**
- Ignorer les erreurs
- Mutations non contrôlées
- Requêtes sans debounce/throttle
- Exposition de tokens dans le code
- Absence de feedback utilisateur

## Codes d'Erreur gRPC

Mapping pour l'UI:

```javascript
const ERROR_MESSAGES = {
  3: 'Données invalides',
  5: 'Ressource non trouvée',
  7: 'Accès refusé',
  16: 'Authentification requise',
  14: 'Service indisponible',
};

function handleGrpcError(err) {
  const code = err.code;
  const message = ERROR_MESSAGES[code] || 'Erreur inconnue';
  return { code, message };
}
```

## Résumé

- gRPC-Web permet gRPC dans le navigateur
- Proxy Envoy requis entre React et backend
- Protobuf génère code client JavaScript
- Patterns React standard s'appliquent
- Gestion erreurs cruciale pour UX

**Prêt à construire votre client React gRPC!** 🚀
