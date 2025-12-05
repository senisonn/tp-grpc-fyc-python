// Simple User Display Component
import React, { useEffect, useState } from 'react';
import { UserServiceClient } from '../generated/user_grpc_web_pb';
import { GetUserRequest } from '../generated/user_pb';

const client = new UserServiceClient('http://localhost:8080');

export default function SimpleUser({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    const request = new GetUserRequest();
    request.setUserId(userId);
    client.getUser(request, {}, (err, response) => {
      if (!err) setUser(response.toObject());
    });
  }, [userId]);
  
  return user ? <div>{user.name} - {user.email}</div> : <div>Loading...</div>;
}
