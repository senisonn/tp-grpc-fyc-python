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
