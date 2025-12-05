// Context Provider
import React, { createContext, useContext } from 'react';
import { UserServiceClient } from '../generated/user_grpc_web_pb';

const GrpcContext = createContext();
export const GrpcProvider = ({children}) => (
  <GrpcContext.Provider value={new UserServiceClient('http://localhost:8080')}>
    {children}
  </GrpcContext.Provider>
);
export const useGrpcClient = () => useContext(GrpcContext);
