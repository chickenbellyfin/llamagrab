

import React, { createContext, useContext, useEffect, useState } from "react"
import { Navigate, useLocation } from "react-router-dom";
import { API, UserAccount } from "./api";
import { AuthPermissions, getPermissions } from "./permissions";

type AuthContext = {
  firstLoad: boolean,
  user?: UserAccount,
  login: (user: UserAccount) => void
  logout: () => void,
  refresh: () => void,
  permissions: AuthPermissions
}

const authContext = createContext<AuthContext>({
  firstLoad: true,
  login: () => {},
  logout: () => {},
  refresh: () => {},
  permissions: getPermissions(undefined)
});

// https://usehooks.com/useAuth/
function useAuth() {
  return useContext(authContext);
}


type ProvideAuthState = {
  firstLoad: boolean,
  user?: UserAccount
}

function useProvideAuth(): AuthContext {
  const [state, setState] = useState<ProvideAuthState>({
    firstLoad: true,
    user: undefined
  })

  const login = (user: UserAccount) => {
    setState({
      firstLoad: false,
      user: user
    })
  }

  const logout = () => {
    setState({
      firstLoad: false,
      user: undefined
    })
  }

  const refresh = () => {
    API.Account.getUser().then(login)
  }

  return {
    firstLoad: state.firstLoad,
    user: state.user,
    login,
    logout,
    refresh,
    permissions: getPermissions(state.user)
  };

}

function ProvideAuth({ children }: any) {
  const auth = useProvideAuth();

  useEffect(() => {
    if (!getToken()) {
      auth.logout()
    } else if (!auth.user) {
      API.Account.getUser()
        .then(auth.login)
        .catch(auth.logout);
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
  const location = useLocation();
  console.log(location.pathname)
  if (auth.user) {
    return <>{props.children}</>
  } else {
    return <Navigate to='/'/>
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