# Guide Complet : React avec gRPC-Web

**Formation gRPC - Séquence 6 : Intégration Front-End**

---

## Table des Matières

1. [Setup du Projet React](#1-setup-du-projet-react)
2. [Import des Stubs Générés](#2-import-des-stubs-générés)
3. [Créer un Client gRPC](#3-créer-un-client-grpc)
4. [Hooks React pour gRPC](#4-hooks-react-pour-grpc)
5. [Gestion des États](#5-gestion-des-états)
6. [Streaming dans React](#6-streaming-dans-react)
7. [Patterns Avancés](#7-patterns-avancés)
8. [Production Best Practices](#8-production-best-practices)

---

## 1. Setup du Projet React

### 1.1 Créer un Nouveau Projet

**Option 1 : Create React App (Classique)**

```bash
# Créer le projet
npx create-react-app my-grpc-web-app
cd my-grpc-web-app

# Installer les dépendances gRPC-Web
npm install grpc-web google-protobuf
```

**Option 2 : Vite (Moderne, Recommandé)**

```bash
# Créer avec Vite
npm create vite@latest my-grpc-web-app -- --template react-ts
cd my-grpc-web-app

# Installer dépendances
npm install
npm install grpc-web google-protobuf
```

### 1.2 Structure du Projet

```
my-grpc-web-app/
├── public/
├── src/
│   ├── proto/              # Stubs générés (à créer)
│   │   ├── user_pb.js
│   │   └── user_grpc_web_pb.js
│   ├── services/           # Clients gRPC
│   │   └── userService.js
│   ├── hooks/              # Custom hooks
│   │   └── useGrpcQuery.js
│   ├── components/         # Composants React
│   │   └── UserProfile.jsx
│   ├── App.jsx
│   └── index.jsx
├── package.json
└── .env                    # Variables d'environnement
```

### 1.3 Configuration des Variables d'Environnement

**Fichier : `.env`**

```bash
# URL du proxy Envoy
REACT_APP_GRPC_WEB_URL=http://localhost:8080

# Pour production
# REACT_APP_GRPC_WEB_URL=https://api.mycompany.com
```

**Fichier : `.env.development`**

```bash
REACT_APP_GRPC_WEB_URL=http://localhost:8080
REACT_APP_ENABLE_GRPC_LOGS=true
```

**Fichier : `.env.production`**

```bash
REACT_APP_GRPC_WEB_URL=https://api.mycompany.com
REACT_APP_ENABLE_GRPC_LOGS=false
```

### 1.4 Générer les Stubs JavaScript/TypeScript

**Prérequis :**

```bash
# Installer protoc
# macOS
brew install protobuf

# Linux
sudo apt-get install protobuf-compiler

# Installer le plugin gRPC-Web
# Télécharger depuis: https://github.com/grpc/grpc-web/releases
# Exemple pour Linux:
wget https://github.com/grpc/grpc-web/releases/download/1.4.2/protoc-gen-grpc-web-1.4.2-linux-x86_64
chmod +x protoc-gen-grpc-web-1.4.2-linux-x86_64
sudo mv protoc-gen-grpc-web-1.4.2-linux-x86_64 /usr/local/bin/protoc-gen-grpc-web
```

**Script de génération : `generate-proto.sh`**

```bash
#!/bin/bash

PROTO_DIR="./proto"
OUT_DIR="./src/proto"

mkdir -p $OUT_DIR

# Générer les stubs JavaScript
protoc \
  --js_out=import_style=commonjs:$OUT_DIR \
  --grpc-web_out=import_style=commonjs,mode=grpcwebtext:$OUT_DIR \
  -I=$PROTO_DIR \
  $PROTO_DIR/*.proto

echo "✓ Stubs generated in $OUT_DIR"
```

**Exemple de fichier `.proto` :**

```protobuf
syntax = "proto3";

package user;

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}

message GetUserRequest {
  string user_id = 1;
}

message GetUserResponse {
  User user = 1;
}

message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message CreateUserResponse {
  User user = 1;
}
```

---

## 2. Import des Stubs Générés

### 2.1 Structure des Fichiers Générés

Après génération, vous aurez :

```
src/proto/
├── user_pb.js              # Messages (User, GetUserRequest, etc.)
└── user_grpc_web_pb.js     # Service client (UserServiceClient)
```

### 2.2 Import dans React

**Fichier : `src/services/userService.js`**

```javascript
// Import des messages
import { 
  GetUserRequest, 
  ListUsersRequest,
  CreateUserRequest 
} from '../proto/user_pb';

// Import du client de service
import { UserServiceClient } from '../proto/user_grpc_web_pb';

// Créer l'instance du client
const client = new UserServiceClient(
  process.env.REACT_APP_GRPC_WEB_URL,  // URL d'Envoy
  null,                                 // Credentials (null pour l'instant)
  null                                  // Options
);

export default client;
export { 
  GetUserRequest, 
  ListUsersRequest,
  CreateUserRequest 
};
```

---

## 3. Créer un Client gRPC

### 3.1 Client de Base

**Fichier : `src/services/grpcClient.js`**

```javascript
import { UserServiceClient } from '../proto/user_grpc_web_pb';
import { grpc } from '@improbable-eng/grpc-web';

// Configuration du client
const grpcURL = process.env.REACT_APP_GRPC_WEB_URL || 'http://localhost:8080';

// Options du client
const clientOptions = {
  // Mode de transport
  // 'grpcwebtext' (base64) ou 'grpcweb' (binaire)
  transport: grpc.CrossBrowserHttpTransport({
    withCredentials: false  // true si vous utilisez des cookies
  })
};

// Créer le client
const userClient = new UserServiceClient(grpcURL, null, clientOptions);

export { userClient };
```

### 3.2 Client avec Authentification

```javascript
import { UserServiceClient } from '../proto/user_grpc_web_pb';

const grpcURL = process.env.REACT_APP_GRPC_WEB_URL;

// Fonction pour obtenir le token JWT
const getAuthToken = () => {
  return localStorage.getItem('jwt_token');
};

// Métadonnées avec authentification
const getMetadata = () => {
  const token = getAuthToken();
  return {
    'authorization': `Bearer ${token}`,
    'x-api-key': 'your-api-key'  // Si applicable
  };
};

// Client avec authentification
class AuthenticatedUserClient {
  constructor() {
    this.client = new UserServiceClient(grpcURL);
  }

  // Wrapper pour appels authentifiés
  getUser(request, callback) {
    this.client.getUser(request, getMetadata(), callback);
  }

  listUsers(request, callback) {
    this.client.listUsers(request, getMetadata(), callback);
  }

  createUser(request, callback) {
    this.client.createUser(request, getMetadata(), callback);
  }
}

export default new AuthenticatedUserClient();
```

### 3.3 Client avec Gestion d'Erreurs

```javascript
import { grpc } from '@improbable-eng/grpc-web';

// Utility pour extraire les erreurs
const extractGrpcError = (error) => {
  if (!error) return 'Unknown error';
  
  // Code d'erreur gRPC
  const code = error.code || grpc.Code.Unknown;
  const message = error.message || 'No error message';
  
  // Mapping des codes gRPC vers messages user-friendly
  const errorMessages = {
    [grpc.Code.NotFound]: 'Resource not found',
    [grpc.Code.PermissionDenied]: 'Permission denied',
    [grpc.Code.Unauthenticated]: 'Not authenticated',
    [grpc.Code.InvalidArgument]: 'Invalid input',
    [grpc.Code.Internal]: 'Internal server error',
    [grpc.Code.Unavailable]: 'Service unavailable'
  };
  
  return errorMessages[code] || message;
};

// Client avec gestion d'erreurs
class GrpcClient {
  constructor(ServiceClient, url) {
    this.client = new ServiceClient(url);
  }

  // Promise wrapper
  async call(method, request, metadata = {}) {
    return new Promise((resolve, reject) => {
      this.client[method](request, metadata, (error, response) => {
        if (error) {
          const userMessage = extractGrpcError(error);
          reject(new Error(userMessage));
        } else {
          resolve(response);
        }
      });
    });
  }
}

export { GrpcClient, extractGrpcError };
```

---

## 4. Hooks React pour gRPC

### 4.1 Hook de Base : `useGrpcQuery`

**Fichier : `src/hooks/useGrpcQuery.js`**

```javascript
import { useState, useEffect } from 'react';

/**
 * Hook pour effectuer des appels gRPC avec gestion d'état
 * 
 * @param {Function} grpcCall - Fonction qui effectue l'appel gRPC
 * @param {Object} request - Requête gRPC
 * @param {Object} options - Options (skip, refetchInterval, etc.)
 */
export const useGrpcQuery = (grpcCall, request, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { 
    skip = false,           // Ne pas exécuter automatiquement
    refetchInterval = 0,    // Refetch automatique (ms)
    onSuccess,              // Callback succès
    onError                 // Callback erreur
  } = options;

  // Fonction pour refetch manuellement
  const refetch = async () => {
    if (skip) return;

    setLoading(true);
    setError(null);

    try {
      const response = await new Promise((resolve, reject) => {
        grpcCall(request, {}, (err, resp) => {
          if (err) reject(err);
          else resolve(resp);
        });
      });

      setData(response);
      if (onSuccess) onSuccess(response);
    } catch (err) {
      setError(err.message || 'An error occurred');
      if (onError) onError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();

    // Refetch interval
    if (refetchInterval > 0) {
      const interval = setInterval(refetch, refetchInterval);
      return () => clearInterval(interval);
    }
  }, [JSON.stringify(request), skip]);

  return { data, loading, error, refetch };
};
```

**Utilisation :**

```javascript
import { useGrpcQuery } from './hooks/useGrpcQuery';
import { userClient } from './services/grpcClient';
import { GetUserRequest } from './proto/user_pb';

function UserProfile({ userId }) {
  // Créer la requête
  const request = new GetUserRequest();
  request.setUserId(userId);

  // Utiliser le hook
  const { data, loading, error, refetch } = useGrpcQuery(
    userClient.getUser.bind(userClient),
    request,
    {
      onSuccess: (response) => console.log('User loaded:', response.toObject()),
      refetchInterval: 30000  // Refetch toutes les 30 secondes
    }
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return null;

  const user = data.getUser();

  return (
    <div>
      <h1>{user.getName()}</h1>
      <p>Email: {user.getEmail()}</p>
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

### 4.2 Hook pour Mutations : `useGrpcMutation`

**Fichier : `src/hooks/useGrpcMutation.js`**

```javascript
import { useState } from 'react';

/**
 * Hook pour les opérations de mutation (create, update, delete)
 */
export const useGrpcMutation = (grpcCall, options = {}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const { onSuccess, onError } = options;

  const mutate = async (request) => {
    setLoading(true);
    setError(null);

    try {
      const response = await new Promise((resolve, reject) => {
        grpcCall(request, {}, (err, resp) => {
          if (err) reject(err);
          else resolve(resp);
        });
      });

      setData(response);
      if (onSuccess) onSuccess(response);
      return response;
    } catch (err) {
      const errorMessage = err.message || 'Mutation failed';
      setError(errorMessage);
      if (onError) onError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
    setLoading(false);
  };

  return { mutate, loading, error, data, reset };
};
```

**Utilisation :**

```javascript
import { useGrpcMutation } from './hooks/useGrpcMutation';
import { userClient } from './services/grpcClient';
import { CreateUserRequest } from './proto/user_pb';

function CreateUserForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const { mutate, loading, error, data } = useGrpcMutation(
    userClient.createUser.bind(userClient),
    {
      onSuccess: (response) => {
        alert('User created!');
        setName('');
        setEmail('');
      },
      onError: (err) => {
        console.error('Failed to create user:', err);
      }
    }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();

    const request = new CreateUserRequest();
    request.setName(name);
    request.setEmail(email);

    try {
      await mutate(request);
    } catch (err) {
      // Error handled by hook
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name"
        required
      />
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create User'}
      </button>
      {error && <div className="error">{error}</div>}
      {data && <div className="success">User created successfully!</div>}
    </form>
  );
}
```

---

## 5. Gestion des États

### 5.1 Pattern Loading/Error/Success

```javascript
function UserComponent({ userId }) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    const request = new GetUserRequest();
    request.setUserId(userId);

    setState(prev => ({ ...prev, loading: true, error: null }));

    userClient.getUser(request, {}, (error, response) => {
      if (error) {
        setState({ data: null, loading: false, error: error.message });
      } else {
        setState({ data: response, loading: false, error: null });
      }
    });
  }, [userId]);

  // Render différents états
  if (state.loading) {
    return (
      <div className="loading-spinner">
        <Spinner />
        <p>Loading user data...</p>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="error-container">
        <ErrorIcon />
        <p>Error: {state.error}</p>
        <button onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  if (!state.data) {
    return <div>No data available</div>;
  }

  const user = state.data.getUser();

  return (
    <div className="user-card">
      <h2>{user.getName()}</h2>
      <p>{user.getEmail()}</p>
    </div>
  );
}
```

### 5.2 Avec Context API (Global State)

**Fichier : `src/context/GrpcContext.jsx`**

```javascript
import { createContext, useContext, useState } from 'react';

const GrpcContext = createContext();

export function GrpcProvider({ children }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const request = new ListUsersRequest();
      request.setPage(1);
      request.setPageSize(50);

      const response = await new Promise((resolve, reject) => {
        userClient.listUsers(request, {}, (err, resp) => {
          if (err) reject(err);
          else resolve(resp);
        });
      });

      setUsers(response.getUsersList());
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const value = {
    users,
    loading,
    loadUsers
  };

  return (
    <GrpcContext.Provider value={value}>
      {children}
    </GrpcContext.Provider>
  );
}

export const useGrpc = () => {
  const context = useContext(GrpcContext);
  if (!context) {
    throw new Error('useGrpc must be used within GrpcProvider');
  }
  return context;
};
```

**Utilisation :**

```javascript
// App.jsx
import { GrpcProvider } from './context/GrpcContext';

function App() {
  return (
    <GrpcProvider>
      <UserList />
    </GrpcProvider>
  );
}

// UserList.jsx
import { useGrpc } from './context/GrpcContext';

function UserList() {
  const { users, loading, loadUsers } = useGrpc();

  useEffect(() => {
    loadUsers();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.getId()}>
          {user.getName()} - {user.getEmail()}
        </li>
      ))}
    </ul>
  );
}
```

---

## 6. Streaming dans React

### 6.1 Server Streaming

```javascript
import { useState, useEffect, useRef } from 'react';

function LogStreamComponent() {
  const [logs, setLogs] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const streamRef = useRef(null);

  const startStreaming = () => {
    const request = new StreamLogsRequest();
    request.setLevel('INFO');

    setIsStreaming(true);
    setLogs([]);

    // Démarrer le stream
    const stream = logServiceClient.streamLogs(request, {});

    // Écouter les messages
    stream.on('data', (response) => {
      const logEntry = response.getLog();
      setLogs(prev => [...prev, {
        message: logEntry.getMessage(),
        timestamp: logEntry.getTimestamp(),
        level: logEntry.getLevel()
      }]);
    });

    // Gestion des erreurs
    stream.on('error', (error) => {
      console.error('Stream error:', error);
      setIsStreaming(false);
    });

    // Fin du stream
    stream.on('end', () => {
      console.log('Stream ended');
      setIsStreaming(false);
    });

    // Sauvegarder la référence pour pouvoir cancel
    streamRef.current = stream;
  };

  const stopStreaming = () => {
    if (streamRef.current) {
      streamRef.current.cancel();
      streamRef.current = null;
      setIsStreaming(false);
    }
  };

  // Cleanup au démontage
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.cancel();
      }
    };
  }, []);

  return (
    <div>
      <button onClick={startStreaming} disabled={isStreaming}>
        Start Streaming
      </button>
      <button onClick={stopStreaming} disabled={!isStreaming}>
        Stop
      </button>

      <div className="log-container">
        {logs.map((log, index) => (
          <div key={index} className={`log-entry ${log.level.toLowerCase()}`}>
            <span className="timestamp">
              {new Date(log.timestamp * 1000).toLocaleTimeString()}
            </span>
            <span className="level">{log.level}</span>
            <span className="message">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 6.2 Hook pour Server Streaming

**Fichier : `src/hooks/useGrpcStream.js`**

```javascript
import { useState, useEffect, useRef } from 'react';

export const useGrpcStream = (streamCall, request, options = {}) => {
  const [data, setData] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const streamRef = useRef(null);

  const { 
    autoStart = false,
    maxItems = 1000,  // Limite pour éviter trop d'éléments en mémoire
    onData,
    onError,
    onEnd
  } = options;

  const start = () => {
    if (isStreaming) return;

    setIsStreaming(true);
    setError(null);
    setData([]);

    const stream = streamCall(request, {});

    stream.on('data', (response) => {
      setData(prev => {
        const newData = [...prev, response];
        // Limiter le nombre d'items
        if (newData.length > maxItems) {
          return newData.slice(-maxItems);
        }
        return newData;
      });

      if (onData) onData(response);
    });

    stream.on('error', (err) => {
      setError(err.message);
      setIsStreaming(false);
      if (onError) onError(err);
    });

    stream.on('end', () => {
      setIsStreaming(false);
      if (onEnd) onEnd();
    });

    streamRef.current = stream;
  };

  const stop = () => {
    if (streamRef.current) {
      streamRef.current.cancel();
      streamRef.current = null;
      setIsStreaming(false);
    }
  };

  const clear = () => {
    setData([]);
  };

  useEffect(() => {
    if (autoStart) {
      start();
    }

    return () => {
      if (streamRef.current) {
        streamRef.current.cancel();
      }
    };
  }, []);

  return {
    data,
    isStreaming,
    error,
    start,
    stop,
    clear
  };
};
```

**Utilisation :**

```javascript
function RealTimeNotifications() {
  const request = new StreamNotificationsRequest();
  
  const { data, isStreaming, start, stop } = useGrpcStream(
    notificationClient.streamNotifications.bind(notificationClient),
    request,
    {
      autoStart: true,
      maxItems: 50,
      onData: (notification) => {
        // Afficher une notification toast
        toast.info(notification.getMessage());
      }
    }
  );

  return (
    <div>
      <h2>Real-time Notifications</h2>
      {isStreaming ? (
        <button onClick={stop}>Stop</button>
      ) : (
        <button onClick={start}>Start</button>
      )}

      <div className="notifications">
        {data.map((notif, i) => (
          <NotificationCard key={i} notification={notif} />
        ))}
      </div>
    </div>
  );
}
```

---

## 7. Patterns Avancés

### 7.1 Pagination

```javascript
function UserListWithPagination() {
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const request = new ListUsersRequest();
  request.setPage(page);
  request.setPageSize(pageSize);

  const { data, loading, error } = useGrpcQuery(
    userClient.listUsers.bind(userClient),
    request
  );

  if (loading) return <Spinner />;
  if (error) return <Error message={error} />;

  const users = data.getUsersList();
  const total = data.getTotal();
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      <UserList users={users} />
      
      <Pagination>
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Previous
        </button>
        
        <span>Page {page} of {totalPages}</span>
        
        <button 
          onClick={() => setPage(p => p + 1)}
          disabled={page >= totalPages}
        >
          Next
        </button>
      </Pagination>
    </div>
  );
}
```

### 7.2 Optimistic Updates

```javascript
function TodoList() {
  const [todos, setTodos] = useState([]);

  const { mutate: createTodo, loading } = useGrpcMutation(
    todoClient.createTodo.bind(todoClient),
    {
      onSuccess: (response) => {
        // La vraie réponse du serveur
        const serverTodo = response.getTodo();
        
        // Mettre à jour avec les données du serveur
        setTodos(prev => 
          prev.map(todo => 
            todo.tempId === serverTodo.getTempId()
              ? serverTodo
              : todo
          )
        );
      },
      onError: (error) => {
        // Rollback en cas d'erreur
        setTodos(prev => prev.filter(todo => !todo.isOptimistic));
        alert('Failed to create todo');
      }
    }
  );

  const addTodo = async (text) => {
    // Créer un todo temporaire (optimistic)
    const tempTodo = {
      tempId: Date.now(),
      text,
      completed: false,
      isOptimistic: true  // Flag pour indiquer que c'est temporaire
    };

    // Ajouter immédiatement à l'UI
    setTodos(prev => [...prev, tempTodo]);

    // Envoyer au serveur
    const request = new CreateTodoRequest();
    request.setText(text);
    request.setTempId(tempTodo.tempId);

    try {
      await createTodo(request);
    } catch (err) {
      // L'erreur est gérée par le hook
    }
  };

  return (
    <div>
      <input 
        type="text" 
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            addTodo(e.target.value);
            e.target.value = '';
          }
        }}
      />

      <ul>
        {todos.map((todo, i) => (
          <li key={todo.id || todo.tempId}>
            {todo.text}
            {todo.isOptimistic && <Spinner size="small" />}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 7.3 Retry avec Exponential Backoff

```javascript
const retryWithBackoff = async (fn, maxRetries = 3) => {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Pas de retry pour certaines erreurs
      if (error.code === grpc.Code.Unauthenticated) {
        throw error;
      }
      
      // Calculer le délai (exponential backoff)
      const delay = Math.min(1000 * Math.pow(2, i), 10000);
      
      console.log(`Retry ${i + 1}/${maxRetries} after ${delay}ms`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
};

// Utilisation
function RobustComponent() {
  const loadData = async () => {
    await retryWithBackoff(async () => {
      const request = new GetDataRequest();
      
      return new Promise((resolve, reject) => {
        client.getData(request, {}, (err, resp) => {
          if (err) reject(err);
          else resolve(resp);
        });
      });
    });
  };

  // ...
}
```

---

## 8. Production Best Practices

### 8.1 Error Boundaries

```javascript
class GrpcErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('gRPC Error:', error, errorInfo);
    
    // Envoyer à un service de monitoring
    // logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Utilisation
function App() {
  return (
    <GrpcErrorBoundary>
      <UserDashboard />
    </GrpcErrorBoundary>
  );
}
```

### 8.2 Request Cancellation

```javascript
function SearchComponent() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    // Cancel requête précédente
    if (abortControllerRef.current) {
      abortControllerRef.current.cancel();
    }

    if (!query) {
      setResults([]);
      return;
    }

    // Créer nouvelle requête
    const request = new SearchRequest();
    request.setQuery(query);

    const call = searchClient.search(request, {});
    
    call.on('data', (response) => {
      setResults(response.getResultsList());
    });

    call.on('error', (error) => {
      if (error.code !== grpc.Code.Cancelled) {
        console.error('Search error:', error);
      }
    });

    abortControllerRef.current = call;

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.cancel();
      }
    };
  }, [query]);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      <SearchResults results={results} />
    </div>
  );
}
```

### 8.3 Monitoring et Logging

```javascript
// Wrapper client avec logging
class MonitoredGrpcClient {
  constructor(client, serviceName) {
    this.client = client;
    this.serviceName = serviceName;
  }

  wrapMethod(methodName) {
    return (request, metadata, callback) => {
      const startTime = Date.now();

      // Log la requête
      console.log(`[gRPC] ${this.serviceName}.${methodName} - Request`, {
        timestamp: new Date().toISOString(),
        request: request.toObject()
      });

      // Exécuter l'appel original
      this.client[methodName](request, metadata, (error, response) => {
        const duration = Date.now() - startTime;

        if (error) {
          // Log l'erreur
          console.error(`[gRPC] ${this.serviceName}.${methodName} - Error`, {
            timestamp: new Date().toISOString(),
            duration: `${duration}ms`,
            error: error.message,
            code: error.code
          });

          // Envoyer à un service de monitoring (ex: Sentry)
          // Sentry.captureException(error);
        } else {
          // Log le succès
          console.log(`[gRPC] ${this.serviceName}.${methodName} - Success`, {
            timestamp: new Date().toISOString(),
            duration: `${duration}ms`
          });
        }

        callback(error, response);
      });
    };
  }
}

// Utilisation
const monitoredClient = new MonitoredGrpcClient(userClient, 'UserService');
const getUser = monitoredClient.wrapMethod('getUser');
```

---

## Conclusion

Ce guide a couvert :

1. ✅ Setup complet d'un projet React avec gRPC-Web
2. ✅ Génération et import des stubs
3. ✅ Création de clients gRPC (simple, authentifié, avec erreurs)
4. ✅ Hooks custom (`useGrpcQuery`, `useGrpcMutation`, `useGrpcStream`)
5. ✅ Gestion des états (loading, error, success)
6. ✅ Streaming server-side dans React
7. ✅ Patterns avancés (pagination, optimistic updates, retry)
8. ✅ Best practices production

**Ressources complémentaires :**
- [gRPC-Web documentation](https://github.com/grpc/grpc-web)
- [React documentation](https://react.dev)
- [Exemples complets dans ce repository](../05-react-integration/examples/)

---

**Guide créé pour la Formation gRPC - Séquence 6**  
**Durée de lecture estimée :** 1h30  
**Niveau :** Intermédiaire à Avancé

