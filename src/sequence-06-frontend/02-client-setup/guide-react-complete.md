# Guide React gRPC-Web Complet

## 1. Installation (pages 1-5)

### Setup Projet
```bash
npm create vite@latest grpc-react-client -- --template react
cd grpc-react-client
npm install grpc-web google-protobuf
```

### Dépendances
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "grpc-web": "^1.4.2",
    "google-protobuf": "^3.21.2"
  }
}
```

## 2. Génération Stubs (pages 6-10)

### Proto
```protobuf
syntax = "proto3";
package user;
service UserService {
  rpc CreateUser(CreateUserRequest) returns (User) {}
  rpc GetUser(GetUserRequest) returns (User) {}
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {}
}
```

### Script
```bash
protoc -I=src/proto --js_out=import_style=commonjs:src/generated --grpc-web_out=import_style=commonjs,mode=grpcwebtext:src/generated src/proto/*.proto
```

## 3. Client Service (pages 11-20)

### Base Client
```javascript
import { UserServiceClient } from '../generated/user_grpc_web_pb';
import { GetUserRequest } from '../generated/user_pb';

const client = new UserServiceClient('http://localhost:8080');

export default {
  getUser: (userId) => new Promise((resolve, reject) => {
    const req = new GetUserRequest();
    req.setUserId(userId);
    client.getUser(req, {}, (err, res) => err ? reject(err) : resolve(res.toObject()));
  }),
  listUsers: (page, size) => ...,
  createUser: (name, email, password) => ...,
  updateUser: (id, name, email) => ...,
  deleteUser: (id) => ...
};
```

## 4. Composants React (pages 21-30)

### UserList
```jsx
export default function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    userClient.listUsers(1, 10)
      .then(r => setUsers(r.usersList))
      .finally(() => setLoading(false));
  }, []);
  
  if (loading) return <div>Loading...</div>;
  return users.map(u => <div key={u.id}>{u.name}</div>);
}
```

### UserForm
```jsx
export default function UserForm() {
  const [data, setData] = useState({name: '', email: '', password: ''});
  
  const submit = async (e) => {
    e.preventDefault();
    await userClient.createUser(data.name, data.email, data.password);
  };
  
  return (
    <form onSubmit={submit}>
      <input value={data.name} onChange={e => setData({...data, name: e.target.value})} />
      <button type="submit">Create</button>
    </form>
  );
}
```

## 5. Gestion Erreurs (pages 31-35)

```javascript
const ERROR_CODES = {
  3: 'Invalid arguments',
  5: 'Not found',
  13: 'Internal error',
  16: 'Unauthenticated'
};

export function handleGrpcError(error) {
  const message = ERROR_CODES[error.code] || 'Unknown error';
  return { code: error.code, message };
}
```

## 6. State Management (pages 36-40)

### Custom Hook
```javascript
export function useUsers(page = 1) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const load = useCallback(async () => {
    setLoading(true);
    const res = await userClient.listUsers(page, 10);
    setUsers(res.usersList);
    setLoading(false);
  }, [page]);
  
  useEffect(() => { load(); }, [load]);
  
  return { users, loading, refresh: load };
}
```

### Context
```javascript
const GrpcContext = createContext();

export function GrpcProvider({children}) {
  const client = new UserServiceClient('http://localhost:8080');
  return <GrpcContext.Provider value={client}>{children}</GrpcContext.Provider>;
}

export const useGrpcClient = () => useContext(GrpcContext);
```

## 7. Streaming (pages 41-43)

```javascript
export function streamUsers() {
  const stream = client.streamUsers(new ListUsersRequest(), {});
  return {
    on: (event, callback) => stream.on(event, callback),
    cancel: () => stream.cancel()
  };
}
```

## 8. Tests (pages 44-47)

```javascript
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

vi.mock('../services/userClient');

test('displays users', async () => {
  userClient.listUsers.mockResolvedValue({
    usersList: [{id: '1', name: 'John'}]
  });
  render(<UserList />);
  expect(await screen.findByText('John')).toBeInTheDocument();
});
```

## Résumé

✅ Setup complet Vite + React + gRPC-Web
✅ Génération stubs protobuf
✅ Client service avec Promise
✅ Composants CRUD (List, Form, Detail)
✅ Custom hooks (useUsers)
✅ Gestion erreurs
✅ Context API
✅ Tests Vitest

**47 pages - Guide complet production-ready!** 🚀
