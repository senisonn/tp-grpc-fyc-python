# Guide Complet : Envoy Proxy pour gRPC-Web

**Formation gRPC - Séquence 6 : Intégration Front-End**

---

## Table des Matières

1. [Introduction à Envoy Proxy](#1-introduction-à-envoy-proxy)
2. [Installation et Prérequis](#2-installation-et-prérequis)
3. [Configuration de Base](#3-configuration-de-base)
4. [Filtres gRPC-Web](#4-filtres-grpc-web)
5. [Configuration CORS](#5-configuration-cors)
6. [Routage et Load Balancing](#6-routage-et-load-balancing)
7. [Déploiement en Production](#7-déploiement-en-production)
8. [Troubleshooting et Debugging](#8-troubleshooting-et-debugging)

---

## 1. Introduction à Envoy Proxy

### 1.1 Qu'est-ce qu'Envoy ?

**Envoy** est un proxy réseau moderne et haute performance conçu pour les architectures de microservices. Il a été créé par Lyft et est maintenant un projet de la Cloud Native Computing Foundation (CNCF).

**Caractéristiques principales :**

- **Performance élevée** : Écrit en C++, optimisé pour la latence et le débit
- **Protocoles modernes** : Support natif de HTTP/1.1, HTTP/2, gRPC
- **Observabilité** : Métriques détaillées, tracing, logging
- **Configuration dynamique** : Mise à jour sans redémarrage
- **Extensibilité** : Système de filtres puissant

### 1.2 Pourquoi Envoy pour gRPC-Web ?

gRPC-Web ne peut pas fonctionner directement dans les navigateurs car :

1. **Limitation du protocole** : Les navigateurs ne peuvent pas envoyer de requêtes HTTP/2 brutes
2. **Sécurité** : Les navigateurs imposent des restrictions CORS
3. **API Web** : Pas d'API native pour le framing HTTP/2

**Solution : Envoy comme Proxy**

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │         │              │         │              │
│   Browser    │ HTTP/1.1│    Envoy     │ HTTP/2  │  gRPC Server │
│  (gRPC-Web)  ├────────►│    Proxy     ├────────►│   (Backend)  │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
```

**Envoy traduit :**
- gRPC-Web (HTTP/1.1) → gRPC natif (HTTP/2)
- Gère CORS pour permettre les requêtes cross-origin
- Ajoute les en-têtes nécessaires
- Transforme les formats de message

### 1.3 Alternatives à Envoy

| Proxy | Avantages | Inconvénients |
|-------|-----------|---------------|
| **Envoy** | ✅ Référence pour gRPC-Web<br>✅ Performance<br>✅ Riche en fonctionnalités | ❌ Configuration complexe |
| **nginx** | ✅ Familier<br>✅ Léger | ❌ Support gRPC-Web limité<br>❌ Nécessite module externe |
| **Traefik** | ✅ Configuration simple<br>✅ Auto-discovery | ❌ Moins performant |
| **grpcwebproxy** | ✅ Simple<br>✅ Go-based | ❌ Fonctionnalités limitées |

**Recommandation :** Envoy pour la production, grpcwebproxy pour le développement.

---

## 2. Installation et Prérequis

### 2.1 Prérequis Système

**Systèmes supportés :**
- Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)
- macOS 11+
- Windows (via Docker ou WSL2)

**Ressources minimales :**
- CPU : 2 cores
- RAM : 512 MB (2 GB recommandé pour production)
- Disk : 100 MB

### 2.2 Installation sur différents systèmes

#### Option 1 : Docker (Recommandé)

**Avantages :** Portable, isolation, reproductible

```bash
# Télécharger l'image officielle
docker pull envoyproxy/envoy:v1.28-latest

# Vérifier l'installation
docker run --rm envoyproxy/envoy:v1.28-latest --version
```

**Sortie attendue :**
```
envoy  version: 6d018967f7c71f98918e26d2081ec99c8e77eb0c/1.28.0/Clean/RELEASE/BoringSSL
```

#### Option 2 : Installation Native (Linux)

**Ubuntu/Debian :**

```bash
# Ajouter le repository Envoy
sudo apt-get update
sudo apt-get install -y apt-transport-https gnupg2 curl lsb-release

curl -sL 'https://deb.dl.getenvoy.io/public/gpg.8115BA8E629CC074.key' | \
  sudo gpg --dearmor -o /usr/share/keyrings/getenvoy-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/getenvoy-keyring.gpg] \
  https://deb.dl.getenvoy.io/public/deb/ubuntu $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/getenvoy.list

# Installer Envoy
sudo apt-get update
sudo apt-get install -y getenvoy-envoy

# Vérifier
envoy --version
```

**macOS :**

```bash
# Via Homebrew
brew install envoyproxy/envoy/envoy

# Vérifier
envoy --version
```

#### Option 3 : Compilation depuis les sources

**Uniquement pour des besoins spécifiques !**

```bash
# Clone le repository
git clone https://github.com/envoyproxy/envoy.git
cd envoy

# Build (nécessite Bazel)
bazel build //source/exe:envoy-static

# L'exécutable sera dans bazel-bin/source/exe/envoy-static
```

### 2.3 Vérification de l'Installation

**Test simple :**

```bash
# Créer un fichier de configuration minimal
cat > test-envoy.yaml <<EOF
static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 10000
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          http_filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match:
                  prefix: "/"
                direct_response:
                  status: 200
                  body:
                    inline_string: "Envoy is working!"
EOF

# Lancer Envoy
envoy -c test-envoy.yaml

# Dans un autre terminal, tester
curl http://localhost:10000
# Doit retourner: "Envoy is working!"
```

---

## 3. Configuration de Base

### 3.1 Structure d'un Fichier de Configuration Envoy

Envoy utilise le format **YAML** avec une structure standardisée :

```yaml
# Ressources statiques (définis au démarrage)
static_resources:
  listeners:      # Points d'écoute (ports)
  clusters:       # Services backend
  
# Ressources dynamiques (optionnel, avancé)
dynamic_resources:
  lds_config:     # Listener Discovery Service
  cds_config:     # Cluster Discovery Service
  
# Configuration administrative
admin:
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 9901
```

### 3.2 Configuration Minimale pour gRPC-Web

**Fichier : `envoy-minimal.yaml`**

```yaml
static_resources:
  # 1. LISTENER - Écoute les requêtes HTTP/1.1 depuis le navigateur
  listeners:
  - name: main_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8080  # Port exposé au navigateur
    
    filter_chains:
    - filters:
      # HTTP Connection Manager - Gère les connexions HTTP
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          
          stat_prefix: grpc_web_proxy
          codec_type: AUTO  # Détection automatique HTTP/1.1 ou HTTP/2
          
          # Chaîne de filtres HTTP
          http_filters:
          # Filtre 1 : gRPC-Web (ESSENTIEL)
          - name: envoy.filters.http.grpc_web
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
          
          # Filtre 2 : CORS (ESSENTIEL pour navigateurs)
          - name: envoy.filters.http.cors
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
          
          # Filtre 3 : Router (OBLIGATOIRE, toujours en dernier)
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
          
          # Configuration des routes
          route_config:
            name: local_routes
            virtual_hosts:
            - name: grpc_services
              domains: ["*"]  # Accepte tous les domaines
              
              # CORS configuration
              cors:
                allow_origin_string_match:
                - safe_regex:
                    regex: \*  # DÉVELOPPEMENT SEULEMENT ! Restreindre en prod
                allow_methods: GET, PUT, DELETE, POST, OPTIONS
                allow_headers: keep-alive,user-agent,cache-control,content-type,content-transfer-encoding,custom-header-1,x-accept-content-transfer-encoding,x-accept-response-streaming,x-user-agent,x-grpc-web,grpc-timeout
                max_age: "1728000"
                expose_headers: custom-header-1,grpc-status,grpc-message
              
              # Routes - Dirige vers le backend gRPC
              routes:
              - match:
                  prefix: "/"  # Toutes les requêtes
                  grpc: {}     # Seulement gRPC
                route:
                  cluster: grpc_backend  # Nom du cluster backend
                  timeout: 60s
  
  # 2. CLUSTERS - Définit les services backend
  clusters:
  - name: grpc_backend
    type: STRICT_DNS  # Résolution DNS
    lb_policy: ROUND_ROBIN  # Load balancing
    
    # Protocol HTTP/2 (OBLIGATOIRE pour gRPC)
    typed_extension_protocol_options:
      envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
        "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
        explicit_http_config:
          http2_protocol_options: {}
    
    # Adresse du serveur gRPC
    load_assignment:
      cluster_name: grpc_backend
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: grpc-server  # Hostname du serveur gRPC
                port_value: 50051     # Port gRPC

# Interface d'administration (monitoring)
admin:
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 9901
```

### 3.3 Comprendre les Composants

#### 3.3.1 Listeners

**Rôle :** Point d'entrée pour les connexions

```yaml
listeners:
- name: my_listener
  address:
    socket_address:
      address: 0.0.0.0    # Écoute sur toutes les interfaces
      port_value: 8080    # Port
```

**Options avancées :**

```yaml
- name: tls_listener
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 8443
  filter_chains:
  - transport_socket:  # TLS/SSL
      name: envoy.transport_sockets.tls
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
        common_tls_context:
          tls_certificates:
          - certificate_chain:
              filename: "/etc/envoy/certs/server.crt"
            private_key:
              filename: "/etc/envoy/certs/server.key"
```

#### 3.3.2 Clusters

**Rôle :** Définit les services backend

```yaml
clusters:
- name: my_backend
  type: STRICT_DNS           # Type de découverte
  lb_policy: ROUND_ROBIN     # Politique de load balancing
  
  load_assignment:
    cluster_name: my_backend
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: backend-server
              port_value: 50051
```

**Types de découverte :**

| Type | Usage |
|------|-------|
| `STATIC` | IPs fixes |
| `STRICT_DNS` | Résolution DNS stricte |
| `LOGICAL_DNS` | Résolution DNS logique |
| `EDS` | Endpoint Discovery Service (dynamique) |

**Politiques de load balancing :**

- `ROUND_ROBIN` : Distribution circulaire
- `LEAST_REQUEST` : Moins chargé
- `RANDOM` : Aléatoire
- `RING_HASH` : Hash consistant
- `MAGLEV` : Distribution optimisée

#### 3.3.3 HTTP Filters

**Chaîne de traitement des requêtes :**

```
Requête → Filter 1 → Filter 2 → Filter 3 → Router → Backend
                ↓         ↓         ↓
            gRPC-Web   CORS    Autres
```

**Ordre important !**
1. Filtres de transformation (gRPC-Web)
2. Filtres de sécurité (CORS, Auth)
3. Router (TOUJOURS en dernier)

---

## 4. Filtres gRPC-Web

### 4.1 Le Filtre gRPC-Web

**Configuration de base :**

```yaml
http_filters:
- name: envoy.filters.http.grpc_web
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
```

**Ce que fait ce filtre :**

1. **Détecte les requêtes gRPC-Web**
   - Content-Type : `application/grpc-web` ou `application/grpc-web-text`
   
2. **Traduit le format**
   - gRPC-Web → gRPC natif (HTTP/2)
   - Headers gRPC-Web → Headers gRPC
   
3. **Gère les modes**
   - Mode binaire : `application/grpc-web`
   - Mode texte (base64) : `application/grpc-web-text`

### 4.2 Modes de gRPC-Web

#### Mode Binaire (Recommandé)

**Avantages :**
- Plus compact (30% plus petit que texte)
- Plus rapide (pas de base64 encoding/decoding)

**Usage :**

```javascript
// Client JavaScript
const client = new UserServiceClient('http://localhost:8080', null, {
  'grpc-web.transport-type': 'binary'  // Mode binaire
});
```

#### Mode Texte (Base64)

**Avantages :**
- Compatible avec tous les proxies
- Peut passer les pare-feu stricts

**Usage :**

```javascript
const client = new UserServiceClient('http://localhost:8080', null, {
  'grpc-web.transport-type': 'text'  // Mode texte
});
```

### 4.3 Configuration Avancée du Filtre

```yaml
- name: envoy.filters.http.grpc_web
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
    # Pas de configuration supplémentaire nécessaire généralement
```

**Note :** Le filtre gRPC-Web est simple mais essentiel. La plupart de la configuration se fait dans le router et CORS.

---

## 5. Configuration CORS

### 5.1 Pourquoi CORS est Essentiel

**Problème :** Navigateurs bloquent les requêtes cross-origin par défaut

```
https://my-app.com → http://api.backend.com ❌ BLOQUÉ par défaut
```

**Solution :** Configurer CORS dans Envoy

### 5.2 Configuration CORS de Base

```yaml
cors:
  # Origines autorisées
  allow_origin_string_match:
  - exact: "http://localhost:3000"      # Exact match
  - exact: "https://my-app.com"
  
  # Méthodes HTTP autorisées
  allow_methods: "GET, POST, PUT, DELETE, OPTIONS"
  
  # En-têtes autorisés
  allow_headers: "content-type, x-grpc-web, grpc-timeout"
  
  # En-têtes exposés au client
  expose_headers: "grpc-status, grpc-message"
  
  # Durée de cache de la preflight (secondes)
  max_age: "86400"  # 24 heures
```

### 5.3 Configuration CORS pour Développement

**Accepte toutes les origines (DÉVELOPPEMENT SEULEMENT) :**

```yaml
cors:
  allow_origin_string_match:
  - safe_regex:
      regex: \*  # Attention: TRÈS permissif !
  
  allow_methods: "GET, POST, PUT, DELETE, OPTIONS"
  allow_headers: "*"
  expose_headers: "grpc-status, grpc-message, grpc-status-details-bin"
  max_age: "1728000"  # 20 jours
  allow_credentials: true
```

⚠️ **ATTENTION :** Ne JAMAIS utiliser `*` en production !

### 5.4 Configuration CORS pour Production

**Origines spécifiques :**

```yaml
cors:
  # Liste blanche d'origines
  allow_origin_string_match:
  - exact: "https://app.mycompany.com"
  - exact: "https://admin.mycompany.com"
  - safe_regex:
      regex: "https://.*\\.mycompany\\.com"  # Tous les sous-domaines
  
  # Méthodes strictes
  allow_methods: "GET, POST, OPTIONS"
  
  # En-têtes spécifiques
  allow_headers: |
    content-type,
    x-grpc-web,
    grpc-timeout,
    authorization,
    x-user-agent
  
  # Exposer seulement les headers nécessaires
  expose_headers: "grpc-status, grpc-message"
  
  # Cache raisonnable
  max_age: "3600"  # 1 heure
  
  # Credentials si nécessaire
  allow_credentials: true
```

### 5.5 Headers gRPC-Web Importants

**Headers à autoriser :**

| Header | Rôle |
|--------|------|
| `content-type` | Type de contenu (application/grpc-web) |
| `x-grpc-web` | Identifie une requête gRPC-Web |
| `grpc-timeout` | Timeout de la requête |
| `authorization` | Token d'authentification |
| `x-user-agent` | User agent du client |

**Headers à exposer :**

| Header | Rôle |
|--------|------|
| `grpc-status` | Code de statut gRPC |
| `grpc-message` | Message d'erreur |
| `grpc-status-details-bin` | Détails d'erreur (binaire) |

---

## 6. Routage et Load Balancing

### 6.1 Configuration de Routes

**Route simple :**

```yaml
routes:
- match:
    prefix: "/"
    grpc: {}  # Seulement les requêtes gRPC
  route:
    cluster: grpc_backend
```

**Routes multiples (microservices) :**

```yaml
routes:
# Service utilisateurs
- match:
    prefix: "/user.UserService/"
    grpc: {}
  route:
    cluster: user_service_cluster
    timeout: 30s

# Service produits
- match:
    prefix: "/product.ProductService/"
    grpc: {}
  route:
    cluster: product_service_cluster
    timeout: 60s

# Service de chat (streaming)
- match:
    prefix: "/chat.ChatService/"
    grpc: {}
  route:
    cluster: chat_service_cluster
    timeout: 0s  # Pas de timeout pour streaming
    idle_timeout: 300s
```

### 6.2 Load Balancing

**Configuration du cluster avec plusieurs endpoints :**

```yaml
clusters:
- name: grpc_backend
  type: STRICT_DNS
  lb_policy: ROUND_ROBIN
  
  load_assignment:
    cluster_name: grpc_backend
    endpoints:
    - lb_endpoints:
      # Instance 1
      - endpoint:
          address:
            socket_address:
              address: grpc-server-1
              port_value: 50051
      # Instance 2
      - endpoint:
          address:
            socket_address:
              address: grpc-server-2
              port_value: 50051
      # Instance 3
      - endpoint:
          address:
            socket_address:
              address: grpc-server-3
              port_value: 50051
```

**Stratégies de load balancing :**

```yaml
# Round Robin - Distribution circulaire
lb_policy: ROUND_ROBIN

# Least Request - Moins chargé (recommandé pour gRPC)
lb_policy: LEAST_REQUEST
least_request_lb_config:
  choice_count: 2  # Comparer 2 instances

# Random - Aléatoire (simple et efficace)
lb_policy: RANDOM
```

### 6.3 Health Checks

**Vérifier la santé des backends :**

```yaml
clusters:
- name: grpc_backend
  # ... configuration ...
  
  # Health checking
  health_checks:
  - timeout: 1s
    interval: 5s
    unhealthy_threshold: 2
    healthy_threshold: 2
    
    # gRPC health check protocol
    grpc_health_check:
      service_name: ""  # Service principal
      authority: grpc-server
```

**Comportement :**
- Envoy ping le serveur toutes les 5 secondes
- Si 2 échecs consécutifs → instance marquée unhealthy
- Si 2 succès consécutifs → instance marquée healthy
- Requests ne sont pas envoyées aux instances unhealthy

### 6.4 Circuit Breaking

**Protéger contre les surcharges :**

```yaml
clusters:
- name: grpc_backend
  # ... configuration ...
  
  circuit_breakers:
    thresholds:
    - priority: DEFAULT
      max_connections: 1000        # Max connexions simultanées
      max_pending_requests: 1000   # Max requêtes en attente
      max_requests: 1000           # Max requêtes actives
      max_retries: 3               # Max retry simultanés
```

---

## 7. Déploiement en Production

### 7.1 Configuration TLS/SSL

**Configuration HTTPS :**

```yaml
listeners:
- name: https_listener
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 8443  # HTTPS
  
  filter_chains:
  - transport_socket:
      name: envoy.transport_sockets.tls
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
        
        common_tls_context:
          # Certificats
          tls_certificates:
          - certificate_chain:
              filename: "/etc/envoy/certs/server.crt"
            private_key:
              filename: "/etc/envoy/certs/server.key"
          
          # Protocoles TLS autorisés
          tls_params:
            tls_minimum_protocol_version: TLSv1_2
            tls_maximum_protocol_version: TLSv1_3
          
          # Cipher suites (optionnel, défaut sécurisé)
          # cipher_suites: "..."
    
    filters:
    # ... filtres HTTP comme avant ...
```

**Générer des certificats pour développement :**

```bash
#!/bin/bash
# generate-dev-certs.sh

# Créer le dossier
mkdir -p certs

# Générer la clé privée
openssl genrsa -out certs/server.key 2048

# Générer le certificat auto-signé (365 jours)
openssl req -new -x509 -key certs/server.key \
  -out certs/server.crt -days 365 \
  -subj "/C=FR/ST=Paris/L=Paris/O=MyCompany/CN=localhost"

echo "Certificats générés dans ./certs/"
```

### 7.2 Configuration avec Docker Compose

**Fichier : `docker-compose.yml`**

```yaml
version: '3.8'

services:
  # Proxy Envoy
  envoy:
    image: envoyproxy/envoy:v1.28-latest
    ports:
      - "8080:8080"   # HTTP
      - "8443:8443"   # HTTPS
      - "9901:9901"   # Admin
    volumes:
      - ./envoy.yaml:/etc/envoy/envoy.yaml:ro
      - ./certs:/etc/envoy/certs:ro
    command: ["-c", "/etc/envoy/envoy.yaml"]
    depends_on:
      - grpc-server
    networks:
      - grpc-network

  # Serveur gRPC (backend)
  grpc-server:
    image: my-grpc-server:latest
    ports:
      - "50051:50051"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db
    networks:
      - grpc-network

  # Base de données
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - grpc-network

networks:
  grpc-network:
    driver: bridge

volumes:
  postgres-data:
```

### 7.3 Métriques et Observabilité

**Activer Prometheus :**

```yaml
stats_sinks:
- name: envoy.stat_sinks.prometheus
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.stat_sinks.prometheus.v3.PrometheusStatsSink

admin:
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 9901
```

**Accéder aux métriques :**

```bash
# Stats admin
curl http://localhost:9901/stats

# Format Prometheus
curl http://localhost:9901/stats/prometheus
```

**Métriques importantes :**

```
# Requêtes
http.grpc_web_proxy.downstream_rq_total
http.grpc_web_proxy.downstream_rq_2xx
http.grpc_web_proxy.downstream_rq_5xx

# Latence
http.grpc_web_proxy.downstream_rq_time

# Connexions
listener.0.0.0.0_8080.downstream_cx_total
listener.0.0.0.0_8080.downstream_cx_active

# Cluster health
cluster.grpc_backend.membership_healthy
cluster.grpc_backend.membership_total
```

### 7.4 Logging

**Configuration des logs :**

```yaml
admin:
  access_log:
  - name: envoy.access_loggers.file
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
      path: "/var/log/envoy/access.log"
      format: "[%START_TIME%] \"%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%\" %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION% \"%REQ(X-FORWARDED-FOR)%\" \"%REQ(USER-AGENT)%\" \"%REQ(X-REQUEST-ID)%\" \"%REQ(:AUTHORITY)%\"\n"
```

**Format JSON (pour parsing) :**

```yaml
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/var/log/envoy/access.log"
    log_format:
      json_format:
        time: "%START_TIME%"
        method: "%REQ(:METHOD)%"
        path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
        protocol: "%PROTOCOL%"
        status: "%RESPONSE_CODE%"
        duration: "%DURATION%"
        bytes_sent: "%BYTES_SENT%"
        bytes_received: "%BYTES_RECEIVED%"
        user_agent: "%REQ(USER-AGENT)%"
```

---

## 8. Troubleshooting et Debugging

### 8.1 Problèmes Courants

#### Erreur : "upstream connect error or disconnect/reset before headers"

**Cause :** Envoy ne peut pas se connecter au backend

**Solutions :**

1. **Vérifier que le backend est accessible :**
```bash
# Depuis le container Envoy
docker exec -it envoy ping grpc-server
docker exec -it envoy telnet grpc-server 50051
```

2. **Vérifier la configuration du cluster :**
```yaml
clusters:
- name: grpc_backend
  # Vérifier l'adresse !
  load_assignment:
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: grpc-server  # Doit être résolvable
              port_value: 50051     # Port correct ?
```

#### Erreur CORS : "No 'Access-Control-Allow-Origin' header"

**Cause :** CORS mal configuré

**Solution :**

```yaml
# S'assurer que le filtre CORS est activé
http_filters:
- name: envoy.filters.http.cors
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors

# ET que CORS est configuré dans virtual_hosts
virtual_hosts:
- name: backend
  domains: ["*"]
  cors:
    allow_origin_string_match:
    - safe_regex:
        regex: \*
    allow_methods: GET, POST, OPTIONS
    allow_headers: "*"
```

#### Erreur : "gRPC method not found"

**Cause :** Route incorrecte ou service non implémenté

**Vérifications :**

1. **Vérifier le nom complet du service :**
```protobuf
// user.proto
package user;

service UserService {  // Nom complet : user.UserService
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
}
```

2. **Route correspondante :**
```yaml
routes:
- match:
    prefix: "/user.UserService/"  # Doit matcher package.Service
    grpc: {}
  route:
    cluster: user_backend
```

### 8.2 Outils de Debugging

#### Interface d'Administration

```bash
# Stats générales
curl http://localhost:9901/stats

# Configuration actuelle
curl http://localhost:9901/config_dump

# Clusters
curl http://localhost:9901/clusters

# Listeners
curl http://localhost:9901/listeners

# Logs en temps réel
curl http://localhost:9901/logging
```

#### Augmenter le Niveau de Logs

```yaml
admin:
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 9901

# Lancer Envoy avec logs debug
# envoy -c envoy.yaml --log-level debug
```

**Ou dynamiquement via l'API admin :**

```bash
# Activer debug sur tous les composants
curl -X POST http://localhost:9901/logging?level=debug

# Debug seulement pour HTTP
curl -X POST http://localhost:9901/logging?http=debug
```

#### grpcurl - tester les endpoints

```bash
# Installer grpcurl
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Lister les services
grpcurl -plaintext localhost:50051 list

# Appeler une méthode
grpcurl -plaintext \
  -d '{"user_id": "123"}' \
  localhost:50051 \
  user.UserService/GetUser
```

### 8.3 Checklist de Vérification

**Avant de déployer en production :**

- [ ] CORS configuré avec origines spécifiques (pas `*`)
- [ ] TLS/SSL activé sur le listener
- [ ] Health checks configurés sur les clusters
- [ ] Circuit breakers configurés
- [ ] Timeouts appropriés (pas 0s sauf streaming)
- [ ] Logs activés et centralisés
- [ ] Métriques exportées (Prometheus)
- [ ] Tests de charge effectués
- [ ] Documentation des routes à jour
- [ ] Certificats valides et renouvelables

### 8.4 Commandes Utiles

```bash
# Valider la configuration
envoy --mode validate -c envoy.yaml

# Dry-run (ne démarre pas réellement)
envoy -c envoy.yaml --mode init_only

# Recharger la configuration (signal)
kill -HUP <envoy-pid>

# Arrêt gracieux
kill -TERM <envoy-pid>

# Dans Docker
docker kill --signal=SIGHUP envoy
docker kill --signal=SIGTERM envoy
```

---

## Conclusion

Ce guide a couvert :

1. ✅ Installation d'Envoy
2. ✅ Configuration de base pour gRPC-Web
3. ✅ Filtres essentiels (gRPC-Web, CORS)
4. ✅ Routage et load balancing
5. ✅ Déploiement en production avec TLS
6. ✅ Observabilité (métriques, logs)
7. ✅ Troubleshooting

**Prochaines étapes :**
- Pratiquer avec le lab React + Envoy
- Explorer les configurations avancées (rate limiting, auth)
- Déployer sur Kubernetes avec Envoy Ingress

---

## Ressources Supplémentaires

- **Documentation officielle :** https://www.envoyproxy.io/docs
- **gRPC-Web filter :** https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_web_filter
- **Exemples :** https://github.com/envoyproxy/envoy/tree/main/examples
- **Communauté :** Slack gRPC (#grpc-web channel)

---

**Guide créé pour la Formation gRPC - Séquence 6**  
**Durée de lecture estimée :** 1 heure  
**Niveau :** Intermédiaire

