### Erreurs Fréquentes

1. **Cannot find module `generated`**

   * **Cause :** Stubs JS non générés
   * **Solution :**

     ```bash
     npm run proto
     ```

2. **Connection refused :8080**

   * **Cause :** Proxy Envoy non démarré
   * **Solution :**

     ```bash
     docker-compose up envoy
     ```

3. **CORS error**

   * **Cause :** Configuration CORS Envoy incorrecte
   * **Solution :**

     * Vérifier `allow_origin` dans `envoy.yaml`

4. **Response undefined**

   * **Cause :** Oubli de `.toObject()`
   * **Solution :**

     ```javascript
     response.toObject();
     ```

5. **Hook warnings**

   * **Cause :** Dépendances manquantes dans `useEffect`
   * **Solution :**

     ```javascript
     useEffect(() => {}, [deps]);
     ```

6. **Module not found: grpc-web**

   * **Cause :** Dépendances non installées
   * **Solution :**

     ```bash
     npm install grpc-web google-protobuf
     ```

---

### Outils de Débogage

#### React DevTools

* Installer l’extension navigateur
* Inspecter les composants
* Visualiser `props` et `state` en temps réel

#### Network Tab (Chrome / Firefox)

* Vérifier les requêtes gRPC-Web
* Format :

  ```
  POST /user.UserService/GetUser
  ```
* Codes de statut courants :

  * `0` → OK
  * `2` → UNKNOWN
  * `5` → NOT_FOUND

#### Console Logging

```javascript
console.log('User:', user.toObject());
console.log('Error code:', err.code);
console.log('Error message:', err.message);
```

---

### Fixes Communs

```javascript
// Fix 1 : Async dans useEffect
useEffect(() => {
  async function load() {
    const data = await client.getUser(userId);
    setUser(data);
  }
  load();
}, [userId]);
```

```javascript
// Fix 2 : Error Boundary
class ErrorBoundary extends React.Component {
  componentDidCatch(error) {
    console.error(error);
  }
  render() {
    return this.props.children;
  }
}
```

```javascript
// Fix 3 : Loading state
if (loading) return <div>Loading...</div>;
if (error) return <div>Error: {error.message}</div>;
if (!data) return null;
```

---

### Checklist de Vérification

* ☐ Stubs générés (`ls src/generated/`)
* ☐ Envoy démarré (`docker ps | grep envoy`)
* ☐ Backend actif sur le port `50051`
* ☐ Imports corrects (`from '../generated/...'`)
* ☐ Dépendances installées (`npm list grpc-web`)
* ☐ CORS configuré dans Envoy

---

If you want, I can:

* Convert this into a **Troubleshooting section** for your course
* Align wording with previous activities
* Add **links between errors ↔ fixes**
