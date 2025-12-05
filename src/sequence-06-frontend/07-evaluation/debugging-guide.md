# Debugging React gRPC

## Erreurs Fréquentes

### 1. Cannot find module 'generated'
**Solution:** `npm run proto`

### 2. Connection refused 8080
**Solution:** Start Envoy proxy: `docker-compose up envoy`

### 3. CORS error
**Solution:** Check envoy.yaml CORS config

### 4. Response undefined
**Solution:** Use .toObject() on proto response

### 5. Hook warnings
**Solution:** Add dependencies to useEffect: `useEffect(() => {}, [deps])`

## DevTools

**React DevTools:**
- Install extension
- Inspect components
- View props/state

**Network Tab:**
- Check requests
- Verify gRPC calls
- Check status codes

**Console:**
```javascript
console.log('User:', user.toObject());
console.log('Error code:', err.code);
```

## Common Fixes

```javascript
// Fix 1: Await in useEffect
useEffect(() => {
  async function load() {
    const data = await client.getUser();
    setUser(data);
  }
  load();
}, []);

// Fix 2: Error boundary
class ErrorBoundary extends React.Component {
  componentDidCatch(error) {
    console.error(error);
  }
  render() { return this.props.children; }
}

// Fix 3: Loading state
if (loading) return <div>Loading...</div>;
if (error) return <div>Error: {error.message}</div>;
```
