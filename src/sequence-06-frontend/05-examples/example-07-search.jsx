// Search Filter
import React, { useState, useEffect } from 'react';

export default function UserSearch({ users }) {
  const [query, setQuery] = useState('');
  const [filtered, setFiltered] = useState(users);
  
  useEffect(() => {
    setFiltered(users.filter(u => 
      u.name.toLowerCase().includes(query.toLowerCase()) ||
      u.email.toLowerCase().includes(query.toLowerCase())
    ));
  }, [query, users]);
  
  return (
    <>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search..." />
      {filtered.map(u => <div key={u.id}>{u.name}</div>)}
    </>
  );
}
