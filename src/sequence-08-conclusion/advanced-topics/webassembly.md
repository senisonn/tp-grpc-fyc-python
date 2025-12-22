**Qu'est-ce que WebAssembly (Wasm)?**
- Format binaire portable
- Exécution proche du natif dans le navigateur
- Supporte C/C++, Rust, Go, etc.
- Complément à JavaScript

**Pourquoi gRPC + Wasm?**
1. **Performance** : Code compilé → plus rapide que JS
2. **Réutilisation** : Code backend → frontend
3. **Typage strict** : Protobuf nativement
4. **Sécurité** : Sandbox Wasm

**Architectures possibles:**

**1. Client gRPC en Wasm**
```
┌──────────────────────┐
│   Browser            │
│  ┌────────────────┐  │
│  │  Wasm Module   │  │
│  │  (gRPC Client) │──┼─> Backend gRPC
│  └────────────────┘  │
│         ▲            │
│  ┌──────┴──────┐     │
│  │  JavaScript │     │
│  └─────────────┘     │
└──────────────────────┘
```

**2. Service gRPC en Wasm (Edge computing)**
```
┌────────────┐
│   Client   │
└──────┬─────┘
       │
┌──────▼────────┐
│  Cloudflare   │
│  Workers      │
│  (Wasm gRPC)  │
└──────┬────────┘
       │
┌──────▼────────┐
│   Database    │
└───────────────┘
```

Exemple Rust → Wasm gRPC:

```rust
// Rust code compilé en Wasm
use tonic::Request;
use user_service_client::UserServiceClient;

#[wasm_bindgen]
pub async fn get_user(user_id: String) -> Result<User, JsValue> {
    let mut client = UserServiceClient::connect("http://api.example.com").await?;
    let request = Request::new(GetUserRequest { user_id });
    let response = client.get_user(request).await?;
    Ok(response.into_inner())
}
```

**Use cases:**
- Gaming (real-time multiplayer)
- Video processing (streaming codecs)
- Crypto/Blockchain (calculs intensifs)
- Edge computing (Cloudflare Workers, Fastly)

**Limitations actuelles:**
- Support gRPC-Wasm encore expérimental
- Taille bundle Wasm peut être grande
- Debugging plus complexe

**Futur:**
- WASI (WebAssembly System Interface)
- Support natif gRPC dans Wasm runtime
- Standardisation en cours

**Ressources:**
- [WebAssembly.org](https://webassembly.org/)
- [gRPC-Web Wasm](https://github.com/grpc/grpc-web/tree/master/net/grpc/gateway/examples/wasm)
- [Tonic (Rust gRPC)](https://github.com/hyperium/tonic)