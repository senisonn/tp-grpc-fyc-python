# QCM React gRPC-Web - 15 questions

## Q1: Setup (1pt)
Quelles dépendances installer?
A) grpc-web, google-protobuf ✓
B) grpc, protobuf
C) axios, fetch
D) express, cors

## Q2: Generation (1pt)
Command pour générer stubs JS?
A) npm install proto
B) protoc --js_out --grpc-web_out ✓
C) grpc compile
D) webpack

## Q3: Client (1pt)
Comment créer client?
A) new UserServiceClient(url) ✓
B) fetch(url)
C) axios.create()
D) WebSocket(url)

## Q4: Requête (1pt)
Créer requête GetUser?
A) new GetUserRequest(); req.setUserId(id) ✓
B) {userId: id}
C) JSON.stringify({userId: id})
D) FormData

## Q5: Callback (1pt)
Gérer réponse?
A) client.getUser(req, {}, (err, res) => {}) ✓
B) await client.getUser(req)
C) client.getUser(req).subscribe()
D) client.getUser(req).pipe()

## Q6: useState (1pt)
Hook React correct?
A) const [user, setUser] = useState(null) ✓
B) const user = useState(null)
C) useState user = null
D) let [user] = useState()

## Q7: useEffect (1pt)
Charger données?
A) useEffect(() => {load()}, [deps]) ✓
B) useEffect(load, deps)
C) componentDidMount() {load()}
D) useState(() => load())

## Q8: Erreur NOT_FOUND (1pt)
Code gRPC?
A) 5 ✓
B) 3
C) 13
D) 404

## Q9: Erreur INVALID_ARGUMENT (1pt)
Code?
A) 3 ✓
B) 5
C) 400
D) 16

## Q10: Validation (1pt)
Valider email?
A) /\S+@\S+\.\S+/.test(email) ✓
B) email.includes('@')
C) email.length > 5
D) typeof email === 'string'

## Q11: Pagination (1pt)
State pour page?
A) const [page, setPage] = useState(1) ✓
B) let page = 1
C) var page
D) page = 1

## Q12: Custom Hook (1pt)
Créer hook?
A) function useUsers() { const [users] = useState([]); return users; } ✓
B) const useUsers = new Hook()
C) @hook function users()
D) hook('users')

## Q13: Context (1pt)
Provider pattern?
A) <Context.Provider value={}>{children}</Provider> ✓
B) Context.provide(value, children)
C) provideContext(value)
D) new ContextProvider()

## Q14: Tests (1pt)
Tester composant?
A) render(<Component />); expect(screen.getByText()).toBeInTheDocument() ✓
B) mount(<Component />).find('div')
C) shallow(<Component />)
D) test(<Component />)

## Q15: Proxy (1pt)
Pourquoi Envoy?
A) Convertir HTTP/1.1 ↔ HTTP/2 pour gRPC ✓
B) Load balancing
C) Compression
D) Logging

**Réponses: A,B,A,A,A,A,A,A,A,A,A,A,A,A,A**
