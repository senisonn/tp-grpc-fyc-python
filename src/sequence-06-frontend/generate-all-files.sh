#!/bin/bash

##############################################################################
# Script de génération complète de la Séquence 6
# Crée tous les fichiers manquants pour une livraison complète
##############################################################################

set -e  # Exit on error

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

echo "🚀 Génération complète de la Séquence 6 - Frontend gRPC-Web"
echo "============================================================="

# Couleurs pour l'output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function create_file() {
    local file_path="$1"
    local file_desc="$2"
    
    if [ -f "$file_path" ]; then
        echo -e "${YELLOW}⏭  Skipping (exists): $file_path${NC}"
    else
        echo -e "${BLUE}📝 Creating: $file_desc${NC}"
        mkdir -p "$(dirname "$file_path")"
        # Le contenu sera ajouté par les fonctions spécifiques
    fi
}

##############################################################################
# 1. CONFIGURATIONS ENVOY
##############################################################################

echo -e "\n${GREEN}■ Creating Envoy configurations...${NC}"

# TLS-only configuration
create_file "02-envoy-proxy/configurations/envoy-tls.yaml" "TLS Configuration"
cat > 02-envoy-proxy/configurations/envoy-tls.yaml << 'EOF'
# Configuration Envoy avec TLS uniquement
# Focus sur la sécurité et le chiffrement

static_resources:
  listeners:
  - name: tls_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8443
    
    filter_chains:
    - transport_socket:
        name: envoy.transport_sockets.tls
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
          
          common_tls_context:
            tls_certificates:
            - certificate_chain:
                filename: "/etc/envoy/certs/server.crt"
              private_key:
                filename: "/etc/envoy/certs/server.key"
            
            tls_params:
              tls_minimum_protocol_version: TLSv1_2
              tls_maximum_protocol_version: TLSv1_3
      
      filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          
          stat_prefix: grpc_web_tls
          codec_type: AUTO
          
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
          
          route_config:
            name: local_routes
            virtual_hosts:
            - name: grpc_services
              domains: ["*"]
              
              cors:
                allow_origin_string_match:
                - safe_regex:
                    regex: "https://.*"  # HTTPS seulement
                allow_methods: "GET, POST, OPTIONS"
                allow_headers: "content-type, x-grpc-web, grpc-timeout, authorization"
                expose_headers: "grpc-status, grpc-message"
                max_age: "3600"
              
              routes:
              - match:
                  prefix: "/"
                  grpc: {}
                route:
                  cluster: grpc_backend
                  timeout: 60s
  
  clusters:
  - name: grpc_backend
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    
    typed_extension_protocol_options:
      envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
        "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
        explicit_http_config:
          http2_protocol_options: {}
    
    load_assignment:
      cluster_name: grpc_backend
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: grpc-server
                port_value: 50051

admin:
  address:
    socket_address:
      address: 127.0.0.1
      port_value: 9901
EOF

# README for configurations
create_file "02-envoy-proxy/configurations/README-configuration.md" "Configuration Guide"
cat > 02-envoy-proxy/configurations/README-configuration.md << 'EOF'
# Guide des Configurations Envoy

Ce dossier contient différentes configurations Envoy pour différents cas d'usage.

## Fichiers de Configuration

### 1. `envoy-basic.yaml`
**Usage:** Configuration minimale pour démarrer rapidement

**Caractéristiques:**
- Configuration simple
- Un seul backend
- Pas de TLS
- Idéal pour apprentissage

**Utilisation:**
```bash
docker run -v $(pwd)/envoy-basic.yaml:/etc/envoy/envoy.yaml \
  -p 8080:8080 -p 9901:9901 \
  envoyproxy/envoy:v1.28-latest
```

### 2. `envoy-with-cors.yaml`
**Usage:** Configuration pour développement avec CORS complet

**Caractéristiques:**
- CORS permissif pour développement
- Support localhost sur tous les ports
- Headers étendus
- Retry policy

**Utilisation:**
```bash
docker-compose -f docker-compose-dev.yml up
```

### 3. `envoy-production.yaml`
**Usage:** Configuration sécurisée pour production

**Caractéristiques:**
- TLS/HTTPS obligatoire
- CORS restrictif (origines spécifiques)
- Health checks
- Circuit breakers
- Métriques Prometheus
- Load balancing multi-instances
- Access logging

**Utilisation:**
```bash
# Nécessite certificats TLS
docker-compose -f docker-compose-prod.yml up
```

### 4. `envoy-tls.yaml`
**Usage:** Focus sur TLS/SSL

**Caractéristiques:**
- Configuration TLS détaillée
- Chiffrement fort (TLS 1.2+)
- Exemple de configuration certificats

### 5. `docker-compose-complete.yml`
**Usage:** Stack complète pour production

**Services inclus:**
- Envoy Proxy
- Backend gRPC
- Frontend React
- PostgreSQL
- Redis
- Prometheus
- Grafana

## Choisir la Bonne Configuration

| Situation | Fichier à utiliser |
|-----------|-------------------|
| **Apprentissage gRPC-Web** | `envoy-basic.yaml` |
| **Développement local** | `envoy-with-cors.yaml` + `docker-compose-dev.yml` |
| **Tests d'intégration** | `envoy-with-cors.yaml` |
| **Staging/Production** | `envoy-production.yaml` + `docker-compose-complete.yml` |
| **Configuration TLS seulement** | `envoy-tls.yaml` |

## Configuration Commune

Tous les fichiers partagent cette structure de base:

```yaml
static_resources:
  listeners:    # Point d'entrée (port 8080 ou 8443)
  clusters:     # Backend gRPC (port 50051)

admin:          # Interface admin (port 9901)
```

## Personnalisation

### Changer le port d'écoute

```yaml
listeners:
- address:
    socket_address:
      port_value: 8080  # ← Modifier ici
```

### Changer l'adresse du backend

```yaml
clusters:
- load_assignment:
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: grpc-server  # ← Modifier ici
              port_value: 50051      # ← Et ici
```

### Ajouter des origines CORS

```yaml
cors:
  allow_origin_string_match:
  - exact: "https://my-new-app.com"  # ← Ajouter ici
```

## Génération de Certificats TLS

Pour `envoy-tls.yaml` et `envoy-production.yaml`:

```bash
# Créer le dossier
mkdir -p certs

# Générer clé privée
openssl genrsa -out certs/server.key 2048

# Générer certificat (auto-signé pour dev)
openssl req -new -x509 -key certs/server.key \
  -out certs/server.crt -days 365 \
  -subj "/C=FR/ST=Paris/L=Paris/O=MyCompany/CN=localhost"
```

Pour production, utiliser Let's Encrypt ou un CA commercial.

## Tests

### Vérifier qu'Envoy fonctionne

```bash
# Health check
curl http://localhost:9901/stats

# CORS preflight
curl -X OPTIONS http://localhost:8080/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### Tester une requête gRPC-Web

```bash
# Nécessite grpcurl
grpcurl -plaintext \
  -d '{"name": "test"}' \
  localhost:8080 \
  myservice.MyService/MyMethod
```

## Debugging

### Logs en temps réel

```bash
# Lancer avec logs debug
docker run -v $(pwd)/envoy.yaml:/etc/envoy/envoy.yaml \
  envoyproxy/envoy:v1.28-latest \
  -c /etc/envoy/envoy.yaml --log-level debug
```

### Interface Admin

Ouvrir http://localhost:9901 pour:
- `/stats` - Métriques
- `/clusters` - État des backends
- `/config_dump` - Configuration actuelle

## Ressources

- [Envoy Documentation](https://www.envoyproxy.io/docs/envoy/latest/)
- [gRPC-Web Filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_web_filter)
- [CORS Filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/cors_filter)
EOF

echo -e "${GREEN}✓ Configurations Envoy created${NC}"

##############################################################################
# 2. SCRIPTS DE GÉNÉRATION PROTO
##############################################################################

echo -e "\n${GREEN}■ Creating proto generation scripts...${NC}"

mkdir -p 03-proto-generation/scripts

# JavaScript generation script
cat > 03-proto-generation/scripts/generate-js.sh << 'EOF'
#!/bin/bash

# Script de génération des stubs JavaScript pour gRPC-Web
# Nécessite: protoc, protoc-gen-grpc-web

set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔨 Generating JavaScript stubs for gRPC-Web..."

# Vérifier les prérequis
command -v protoc >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc not found. Please install Protocol Buffers compiler.${NC}" 
    exit 1
}

command -v protoc-gen-grpc-web >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc-gen-grpc-web not found.${NC}"
    echo "Install it from: https://github.com/grpc/grpc-web/releases"
    exit 1
}

# Dossiers
PROTO_DIR="${PROTO_DIR:-./proto}"
OUT_DIR="${OUT_DIR:-./src/proto}"

# Créer le dossier de sortie
mkdir -p "$OUT_DIR"

echo "📂 Proto directory: $PROTO_DIR"
echo "📂 Output directory: $OUT_DIR"

# Générer pour chaque fichier .proto
for proto_file in "$PROTO_DIR"/*.proto; do
    if [ -f "$proto_file" ]; then
        echo "Processing: $(basename "$proto_file")"
        
        protoc \
            --js_out=import_style=commonjs:"$OUT_DIR" \
            --grpc-web_out=import_style=commonjs,mode=grpcwebtext:"$OUT_DIR" \
            -I="$PROTO_DIR" \
            "$proto_file"
    fi
done

echo -e "${GREEN}✓ JavaScript stubs generated successfully!${NC}"
echo "Files created in: $OUT_DIR"
EOF

chmod +x 03-proto-generation/scripts/generate-js.sh

# TypeScript generation script
cat > 03-proto-generation/scripts/generate-ts.sh << 'EOF'
#!/bin/bash

# Script de génération des stubs TypeScript pour gRPC-Web

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔨 Generating TypeScript stubs for gRPC-Web..."

# Vérifier les prérequis
command -v protoc >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc not found${NC}" 
    exit 1
}

command -v protoc-gen-grpc-web >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc-gen-grpc-web not found${NC}"
    exit 1
}

command -v protoc-gen-ts >/dev/null 2>&1 || { 
    echo -e "${RED}❌ protoc-gen-ts not found${NC}"
    echo "Install with: npm install -g ts-protoc-gen"
    exit 1
}

PROTO_DIR="${PROTO_DIR:-./proto}"
OUT_DIR="${OUT_DIR:-./src/proto}"

mkdir -p "$OUT_DIR"

echo "📂 Proto directory: $PROTO_DIR"
echo "📂 Output directory: $OUT_DIR"

for proto_file in "$PROTO_DIR"/*.proto; do
    if [ -f "$proto_file" ]; then
        echo "Processing: $(basename "$proto_file")"
        
        # Generate TypeScript definitions
        protoc \
            --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
            --js_out=import_style=commonjs:"$OUT_DIR" \
            --ts_out=service=grpc-web:"$OUT_DIR" \
            --grpc-web_out=import_style=typescript,mode=grpcwebtext:"$OUT_DIR" \
            -I="$PROTO_DIR" \
            "$proto_file"
    fi
done

echo -e "${GREEN}✓ TypeScript stubs generated successfully!${NC}"
EOF

chmod +x 03-proto-generation/scripts/generate-ts.sh

# package.json for proto generation
cat > 03-proto-generation/scripts/package.json << 'EOF'
{
  "name": "grpc-web-proto-generation",
  "version": "1.0.0",
  "description": "Scripts for generating gRPC-Web stubs",
  "scripts": {
    "generate:js": "./generate-js.sh",
    "generate:ts": "./generate-ts.sh",
    "generate": "npm run generate:ts"
  },
  "devDependencies": {
    "google-protobuf": "^3.21.2",
    "grpc-web": "^1.4.2",
    "ts-protoc-gen": "^0.15.0",
    "typescript": "^5.0.0"
  }
}
EOF

echo -e "${GREEN}✓ Proto generation scripts created${NC}"

##############################################################################
# COMPLETION MESSAGE
##############################################################################

echo ""
echo "============================================================="
echo -e "${GREEN}✓ All files created successfully!${NC}"
echo "============================================================="
echo ""
echo "Next steps:"
echo "1. Review generated files"
echo "2. Generate PDFs from markdown guides"
echo "3. Test configurations with Docker"
echo "4. Upload to GitHub"
echo ""

