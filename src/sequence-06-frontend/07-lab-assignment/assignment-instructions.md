# Lab Pratique: Client React gRPC-Web

**Points**: 30  
**Durée estimée**: 60-90 minutes  
**Type**: Projet à remettre

---

## 🎯 Objectifs

Créer un client React complet utilisant gRPC-Web pour communiquer avec un service de gestion d'utilisateurs.

À la fin de ce lab, vous aurez:
- Configuré Envoy comme proxy gRPC-Web
- Généré des stubs JavaScript depuis des fichiers .proto
- Implémenté un client React avec gRPC-Web
- Géré les erreurs et les états de chargement
- Implémenté du server streaming
- Ajouté l'authentification JWT

---

## 📋 Prérequis

### Outils requis
- [ ] Node.js v18+
- [ ] Docker et Docker Compose
- [ ] protoc et plugin grpc-web
- [ ] Un éditeur de code (VS Code recommandé)

### Connaissances
- [ ] React (hooks, useState, useEffect)
- [ ] JavaScript ES6+ ou TypeScript
- [ ] Promesses et async/await
- [ ] Bases de Docker Compose

---

## 📦 Code de départ

Téléchargez et décompressez le fichier `lab-starter-code.zip`.

Structure:
```
lab-react-grpc/
├── docker-compose.yml      # Stack complète
├── envoy.yaml               # Configuration Envoy de base
├── proto/
│   └── user.proto           # Service à implémenter
├── backend/                 # Backend gRPC fourni
│   └── ...
├── package.json
├── public/
│   └── index.html
└── src/
    ├── index.tsx
    ├── App.tsx              # À compléter
    ├── components/
    │   ├── UserList.tsx     # À créer
    │   ├── UserForm.tsx     # À créer
    │   └── UserStream.tsx   # À créer
    ├── services/
    │   └── userService.ts   # À créer
    ├── hooks/
    │   └── useGrpcClient.ts # À créer
    └── proto/               # Généré par protoc
```

---

## 📝 Partie 1: Configuration Envoy (5 points)

### Tâche 1.1: Compléter envoy.yaml

Le fichier `envoy.yaml` de base est fourni. Vous devez:

1. **Ajouter le filtre CORS** (2 pts)
   ```yaml
   # Dans http_filters, AVANT grpc_web
   - name: envoy.filters.http.cors
     typed_config:
       "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
   ```

2. **Configurer CORS dans virtual_hosts** (2 pts)
   ```yaml
   cors:
     allow_origin_string_match:
     - prefix: "*"  # Dev only
     allow_methods: "GET, POST, PUT, DELETE, OPTIONS"
     allow_headers: "content-type, x-grpc-web, authorization"
     expose_headers: "grpc-status, grpc-message"
   ```

3. **Vérifier la configuration** (1 pt)
   ```bash
   docker-compose up envoy
   # Vérifier: http://localhost:9901
   ```

### Critères d'évaluation (5 pts)
- ✅ Filtre CORS ajouté au bon endroit: 2 pts
- ✅ Configuration CORS complète: 2 pts
- ✅ Envoy démarre sans erreur: 1 pt

---

## 📝 Partie 2: Génération des stubs (5 points)

### Tâche 2.1: Générer les stubs JavaScript

Examinez le fichier `proto/user.proto`:

```protobuf
syntax = "proto3";

package user;

service UserService {
  // Unaire: Récupérer un utilisateur
  rpc GetUser(GetUserRequest) returns (User);
  
  // Unaire: Créer un utilisateur  
  rpc CreateUser(CreateUserRequest) returns (User);
  
  // Server streaming: Stream de tous les utilisateurs
  rpc StreamUsers(StreamUsersRequest) returns (stream User);
}

message GetUserRequest {
  int64 id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message StreamUsersRequest {}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  string created_at = 4;
}
```

### Tâche 2.2: Commande de génération

Créez un script `scripts/generate-proto.sh`:

```bash
#!/bin/bash

protoc -I=./proto user.proto \
  --js_out=import_style=commonjs:./src/proto \
  --grpc-web_out=import_style=typescript,mode=grpcwebtext:./src/proto
```

Exécutez:
```bash
chmod +x scripts/generate-proto.sh
./scripts/generate-proto.sh
```

### Tâche 2.3: Vérifier les fichiers générés

Vous devriez avoir:
- `src/proto/user_pb.js` (messages)
- `src/proto/user_grpc_web_pb.js` (client)

### Critères d'évaluation (5 pts)
- ✅ Script de génération correct: 2 pts
- ✅ Fichiers générés présents: 2 pts
- ✅ Imports fonctionnels dans le code: 1 pt

---

## 📝 Partie 3: Service gRPC (8 points)

### Tâche 3.1: Créer le service userService.ts

Dans `src/services/userService.ts`:

```typescript
import { UserServiceClient } from '../proto/user_grpc_web_pb';
import {
  GetUserRequest,
  CreateUserRequest,
  StreamUsersRequest,
  User
} from '../proto/user_pb';

const client = new UserServiceClient('http://localhost:8080', null, null);

// TODO: Implémenter ces fonctions

export const getUser = async (id: number): Promise<User> => {
  // À implémenter
};

export const createUser = async (name: string, email: string): Promise<User> => {
  // À implémenter
};

export const streamUsers = (
  onData: (user: User) => void,
  onEnd: () => void,
  onError: (error: Error) => void
) => {
  // À implémenter
  // Retourner l'objet stream pour pouvoir l'annuler
};
```

### Implémentation attendue

#### getUser (3 pts)

```typescript
export const getUser = async (id: number): Promise<User> => {
  return new Promise((resolve, reject) => {
    const request = new GetUserRequest();
    request.setId(id);
    
    client.getUser(request, {}, (err, response) => {
      if (err) {
        reject(err);
      } else {
        resolve(response);
      }
    });
  });
};
```

#### createUser (3 pts)

```typescript
export const createUser = async (
  name: string,
  email: string
): Promise<User> => {
  return new Promise((resolve, reject) => {
    const request = new CreateUserRequest();
    request.setName(name);
    request.setEmail(email);
    
    client.createUser(request, {}, (err, response) => {
      if (err) {
        reject(err);
      } else {
        resolve(response);
      }
    });
  });
};
```

#### streamUsers (2 pts)

```typescript
export const streamUsers = (
  onData: (user: User) => void,
  onEnd: () => void,
  onError: (error: Error) => void
) => {
  const request = new StreamUsersRequest();
  const stream = client.streamUsers(request, {});
  
  stream.on('data', (user: User) => {
    onData(user);
  });
  
  stream.on('end', () => {
    onEnd();
  });
  
  stream.on('error', (err: any) => {
    onError(err);
  });
  
  return stream;  // Pour pouvoir annuler: stream.cancel()
};
```

### Critères d'évaluation (8 pts)
- ✅ getUser implémenté correctement: 3 pts
- ✅ createUser implémenté correctement: 3 pts
- ✅ streamUsers implémenté correctement: 2 pts

---

## 📝 Partie 4: Composants React (8 points)

### Tâche 4.1: UserList.tsx (3 pts)

Afficher la liste des utilisateurs et gérer le chargement.

```typescript
import React, { useState, useEffect } from 'react';
import { getUser } from '../services/userService';
import { User } from '../proto/user_pb';

export const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const fetchUser = async (id: number) => {
    setLoading(true);
    setError('');
    
    try {
      const user = await getUser(id);
      setUsers(prev => [...prev, user]);
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Liste des utilisateurs</h2>
      
      <button onClick={() => fetchUser(1)}>
        Charger utilisateur #1
      </button>
      
      {loading && <p>Chargement...</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
      
      <ul>
        {users.map(user => (
          <li key={user.getId()}>
            #{user.getId()} - {user.getName()} ({user.getEmail()})
          </li>
        ))}
      </ul>
    </div>
  );
};
```

### Tâche 4.2: UserForm.tsx (3 pts)

Créer un formulaire pour ajouter un utilisateur.

```typescript
import React, { useState } from 'react';
import { createUser } from '../services/userService';

export const UserForm: React.FC<{ onUserCreated: () => void }> = ({
  onUserCreated
}) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await createUser(name, email);
      setName('');
      setEmail('');
      onUserCreated();
      alert('Utilisateur créé!');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Créer un utilisateur</h2>
      
      <input
        type="text"
        placeholder="Nom"
        value={name}
        onChange={e => setName(e.target.value)}
        required
      />
      
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Création...' : 'Créer'}
      </button>
      
      {error && <p style={{color: 'red'}}>{error}</p>}
    </form>
  );
};
```

### Tâche 4.3: UserStream.tsx (2 pts)

Afficher le stream d'utilisateurs en temps réel.

```typescript
import React, { useState, useEffect } from 'react';
import { streamUsers } from '../services/userService';
import { User } from '../proto/user_pb';

export const UserStream: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [streaming, setStreaming] = useState(false);

  useEffect(() => {
    if (!streaming) return;

    const stream = streamUsers(
      // onData
      (user) => {
        setUsers(prev => [...prev, user]);
      },
      // onEnd
      () => {
        setStreaming(false);
        console.log('Stream terminé');
      },
      // onError
      (error) => {
        console.error('Stream error:', error);
        setStreaming(false);
      }
    );

    // Cleanup: annuler le stream au démontage
    return () => {
      stream.cancel();
    };
  }, [streaming]);

  return (
    <div>
      <h2>Stream d'utilisateurs</h2>
      
      <button onClick={() => setStreaming(!streaming)}>
        {streaming ? 'Arrêter le stream' : 'Démarrer le stream'}
      </button>
      
      <p>Utilisateurs reçus: {users.length}</p>
      
      <ul>
        {users.map((user, idx) => (
          <li key={idx}>
            #{user.getId()} - {user.getName()}
          </li>
        ))}
      </ul>
    </div>
  );
};
```

### Critères d'évaluation (8 pts)
- ✅ UserList avec gestion erreurs/loading: 3 pts
- ✅ UserForm fonctionnel: 3 pts
- ✅ UserStream avec cleanup: 2 pts

---

## 📝 Partie 5: Gestion des erreurs (4 points)

### Tâche 5.1: Error Boundary

Créez un Error Boundary React:

```typescript
// src/components/ErrorBoundary.tsx
import React from 'react';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{padding: '20px', border: '2px solid red'}}>
          <h2>Une erreur est survenue</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Réessayer
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Tâche 5.2: Utiliser l'Error Boundary

Dans `App.tsx`:

```typescript
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        {/* Vos composants */}
      </div>
    </ErrorBoundary>
  );
}
```

### Critères d'évaluation (4 pts)
- ✅ Error Boundary implémenté: 2 pts
- ✅ Gestion des erreurs dans les composants: 2 pts

---

## 🚀 Démarrage et tests

### Démarrer la stack

```bash
# Lancer le backend + Envoy
docker-compose up -d

# Vérifier qu'Envoy tourne
curl http://localhost:9901/ready

# Lancer le frontend React
npm install
npm start

# Ouvrir http://localhost:3000
```

### Tests à effectuer

1. **Test Unaire**: Cliquer sur "Charger utilisateur" → Doit afficher l'utilisateur
2. **Test Création**: Remplir le formulaire → Doit créer l'utilisateur
3. **Test Stream**: Cliquer sur "Démarrer le stream" → Doit recevoir les utilisateurs progressivement
4. **Test Erreur**: Essayer de charger un utilisateur inexistant → Doit afficher une erreur
5. **Test CORS**: Vérifier dans DevTools qu'il n'y a pas d'erreur CORS

---

## 📤 À remettre

### Fichiers à soumettre

Créez un ZIP contenant:
```
lab-react-grpc.zip
├── envoy.yaml (complété)
├── src/
│   ├── services/userService.ts (implémenté)
│   ├── components/
│   │   ├── UserList.tsx
│   │   ├── UserForm.tsx
│   │   ├── UserStream.tsx
│   │   └── ErrorBoundary.tsx
│   ├── App.tsx
│   └── proto/ (généré)
├── scripts/generate-proto.sh
└── README.md (avec instructions de démarrage)
```

### Format de remise

- **Fichier**: `nom-prenom-lab-grpc-web.zip`
- **Taille max**: 10 MB
- **Deadline**: Voir Moodle

---

## 📊 Grille d'évaluation détaillée

| Critère | Points | Description |
|---------|--------|-------------|
| **Envoy CORS** | 2 | Filtre CORS correctement configuré |
| **Envoy Config** | 3 | Configuration complète et fonctionnelle |
| **Génération stubs** | 5 | Scripts corrects, fichiers générés |
| **getUser** | 3 | Implémentation correcte avec gestion erreur |
| **createUser** | 3 | Implémentation correcte avec gestion erreur |
| **streamUsers** | 2 | Stream fonctionnel avec cleanup |
| **UserList** | 3 | Affichage + loading + erreurs |
| **UserForm** | 3 | Formulaire fonctionnel |
| **UserStream** | 2 | Stream React avec cleanup |
| **Error Boundary** | 2 | Boundary implémentée |
| **Gestion erreurs** | 2 | Erreurs gérées dans tous les composants |
| **Total** | **30** | |

### Bonus (non compté dans les 30 pts)
- Authentication JWT (+2 pts)
- Tests unitaires (+3 pts)
- UI/UX soignée (+1 pt)

---

## 💡 Conseils

### Debugging

1. **Envoy ne démarre pas**
   ```bash
   # Vérifier les logs
   docker-compose logs envoy
   ```

2. **Erreurs CORS**
   - Vérifier que le filtre CORS est AVANT grpc_web
   - Vérifier les headers autorisés

3. **Stubs non trouvés**
   ```bash
   # Vérifier la génération
   ls -la src/proto/
   # Devrait montrer user_pb.js et user_grpc_web_pb.js
   ```

4. **Erreurs au runtime**
   - Ouvrir Chrome DevTools
   - Onglet Network: voir les requêtes gRPC-Web
   - Onglet Console: voir les erreurs JS

### Ressources

- Guide Envoy Proxy (PDF)
- Guide React gRPC-Web (PDF)
- Exemples React (dossier examples/)
- Documentation gRPC-Web: https://github.com/grpc/grpc-web

---

**Bonne chance! 🚀**

*Questions? Postez sur le forum du Lab*
