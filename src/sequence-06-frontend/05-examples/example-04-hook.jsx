// Custom Hook
import { useState, useEffect } from 'react';
import userClient from '../services/userClient';

export function useUsers(page = 1, size = 10) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    setLoading(true);
    userClient.listUsers(page, size)
      .then(r => setUsers(r.usersList))
      .finally(() => setLoading(false));
  }, [page, size]);
  
  return { users, loading };
}
