**Qu'est-ce que WebRTC?**
- Web Real-Time Communication
- Peer-to-peer audio/vidéo dans le navigateur
- Pas de serveur intermédiaire (idéalement)
- Utilisé pour: Visio, gaming, IoT

**Pourquoi combiner gRPC et WebRTC?**

1. **Signaling avec gRPC** : Établir connection WebRTC
2. **Contrôle avec gRPC** : Gérer sessions, permissions
3. **Métadonnées avec gRPC** : Échanger infos participants
4. **Fallback avec gRPC** : Si P2P échoue

**Architecture hybride:**
```
┌─────────────┐                      ┌─────────────┐
│  Browser A  │                      │  Browser B  │
└──────┬──────┘                      └──────┬──────┘
       │                                    │
       │ 1. gRPC Signaling                  │
       ├────────────┬───────────────────────┤
       │            │                       │
       │     ┌──────▼──────┐                │
       │     │   Server    │                │
       │     │  gRPC API   │                │
       │     └─────────────┘                │
       │                                    │
       │ 2. WebRTC Direct (P2P)             │
       ◄────────────────────────────────────►
            Audio/Video/Data

```

Flow typique:
Étape 1 : Signaling via gRPC

```py
# Server gRPC
class SignalingService(signaling_pb2_grpc.SignalingServiceServicer):
    def CreateRoom(self, request, context):
        room_id = generate_room_id()
        return Room(id=room_id, created_at=now())
    
    def JoinRoom(self, request, context):
        # Return list of participants
        return Participants(users=[...])
    
    def SendOffer(self, request, context):
        # Exchange SDP offers
        return OfferResponse(...)
```

Étape 2 : Établir WebRTC

```js
// Client JavaScript
const client = new SignalingServiceClient('http://localhost:8080');

// Créer room via gRPC
const room = await client.createRoom({});

// Créer WebRTC peer connection
const pc = new RTCPeerConnection();

// Créer offer
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

// Envoyer offer via gRPC
await client.sendOffer({
  roomId: room.id,
  sdp: offer.sdp
});

// Recevoir answer via gRPC streaming
const stream = client.receiveAnswers({roomId: room.id});
stream.on('data', (answer) => {
  pc.setRemoteDescription(answer.sdp);
});

// WebRTC established!
```


**Use cases:**
- **Visioconférence** : Signaling gRPC + Media WebRTC
- **Gaming multijoueur** : State sync gRPC + Game data WebRTC
- **Collaboration temps réel** : Control gRPC + Data WebRTC
- **IoT streaming** : Commands gRPC + Video WebRTC

**Avantages combinaison:**
- gRPC : Structure, typage, sécurité
- WebRTC : Latence ultra-faible, P2P

**Exemple projet:**
```
video-chat-app/
├── backend/
│   ├── signaling_service.py (gRPC)
│   └── room_manager.py
├── frontend/
│   ├── grpc_client.js (Signaling)
│   └── webrtc_manager.js (Media)
└── proto/
    └── signaling.proto
```

Ressources:

- WebRTC Basics
- gRPC WebRTC Example
- Janus Gateway (Media server)

- [WebRTC Basics](https://webrtc.org/getting-started/overview)
- [gRPC WebRTC Example](https://github.com/muaz-khan/WebRTC-Experiment)
- [Janus Gateway (Media server)](https://janus.conf.meetecho.com/)