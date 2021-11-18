

import React, { createContext, useContext, useEffect, useState } from "react"
import { Navigate } from "react-router-dom";
import { API, User } from "./api";

type AuthContext = {
  user?: User,
  login: (user: User) => void
  logout: () => void
}

const authContext = createContext<AuthContext>({
  login: () => {},
  logout: () => {}
});

// https://usehooks.com/useAuth/
function useAuth() {
  return useContext(authContext);  
}

function useProvideAuth(): AuthContext {
  const [user, setUser] = useState<User>()

  const login = (user: User) => {
    setUser(user)
  }

  const logout = () => {
    setUser(undefined)
  }

  return {
    user,
    login,
    logout
  };

}

function ProvideAuth({ children }: any) {
  const auth = useProvideAuth();

  useEffect(() => {
    if (! auth.user) {
      API.Account.getUser().then(auth.login).catch(() => {})
    }
  }, []);
  
  return (
    <authContext.Provider value={auth}>
      { children }
    </authContext.Provider>
  );
}

const ProtectedRoute: React.FC<{}> = props => {
  const auth = useAuth()
  if (auth.user) {
    return <>{props.children}</>
  } else {
    return <Navigate to='/login'/>
  }
}


function setToken(token: string): void {
  localStorage.setItem('token', JSON.stringify(token))  
}

function deleteToken(): void {
  localStorage.removeItem('token')
}

function getToken(): string | null {
  const token = localStorage.getItem('token')
  if (token) {
    return JSON.parse(token)
  }
  return null
}

export { 
  useAuth,
  ProtectedRoute,
  ProvideAuth,
  setToken, deleteToken, getToken }