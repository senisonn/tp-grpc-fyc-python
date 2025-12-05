// Form Validation
import React, { useState } from 'react';
import userClient from '../services/userClient';

export default function ValidatedForm() {
  const [data, setData] = useState({ name: '', email: '', password: '' });
  const [errors, setErrors] = useState({});
  
  const validate = () => {
    const e = {};
    if (data.name.length < 2) e.name = 'Min 2 chars';
    if (!/\S+@\S+\.\S+/.test(data.email)) e.email = 'Invalid email';
    if (data.password.length < 8) e.password = 'Min 8 chars';
    setErrors(e);
    return Object.keys(e).length === 0;
  };
  
  const submit = async (e) => {
    e.preventDefault();
    if (validate()) await userClient.createUser(data.name, data.email, data.password);
  };
  
  return (
    <form onSubmit={submit}>
      <input value={data.name} onChange={e => setData({...data, name: e.target.value})} />
      {errors.name && <span>{errors.name}</span>}
      <button type="submit">Create</button>
    </form>
  );
}
