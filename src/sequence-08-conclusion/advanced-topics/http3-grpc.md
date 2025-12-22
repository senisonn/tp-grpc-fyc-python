**Qu'est-ce que HTTP/3?**
- Successeur de HTTP/2
- Basé sur QUIC (Quick UDP Internet Connections)
- Transport sur UDP au lieu de TCP
- Développé initialement par Google

**Avantages de HTTP/3:**
1. **0-RTT Connection** : Pas de handshake TCP
2. **Meilleure mobilité** : Survive aux changements réseau
3. **Head-of-line blocking résolu** : Indépendance des streams
4. **Encryption native** : TLS 1.3 intégré
5. **Performance mobile** : Meilleur sur réseaux instables

**gRPC + HTTP/3:**
```
Aujourd'hui:
gRPC → HTTP/2 → TCP → IP

Futur:
gRPC → HTTP/3 → QUIC (UDP) → IP
```

**Bénéfices pour gRPC:**

- Latence réduite (~15-30%)
- Meilleure résilience réseau
- Streaming plus robuste
- Mobilité améliorée

**État actuel (2024-2025):**

- ⚠️ Support expérimental dans gRPC-core
- ✅ Chrome, Firefox supportent HTTP/3
- ✅ Cloudflare, Google Cloud utilisent HTTP/3
- 🔄 Adoption progressive

**Exemple configuration (expérimental):**

```py
# gRPC avec HTTP/3 (futur)
import grpc

channel_credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel(
    'api.example.com:443',
    channel_credentials,
    options=[
        ('grpc.http_version', '3'),  # Expérimental
        ('grpc.enable_quic', True)
    ]
)
```

**Ressources:**
- [HTTP/3 explained](https://http3-explained.haxx.se/)
- [QUIC protocol](https://www.chromium.org/quic/)
- [gRPC HTTP/3 proposal](https://github.com/grpc/grpc/blob/master/doc/core/grpc-on-http3.md)