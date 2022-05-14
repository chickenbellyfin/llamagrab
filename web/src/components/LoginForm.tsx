import { useState } from 'react';
import { setToken, useAuth } from '../auth'
import { Typography } from 'antd'
import { useNavigate } from 'react-router';
import { API } from '../api';
import CredentialsForm from './CredentialsForm';
import { Link } from 'react-router-dom';

const { Text } = Typography;

type LoginResponse = {
  access_token: string,
  token_type: string,
}

async function doLogin(
  username: string,
  password: string,
  ): Promise<LoginResponse> {
  return fetch('/api/account/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      'username': username,
      'password': password,

    })
  }).then(response => {
    if (!response.ok) {
      throw response;
    }
    return response.json() as Promise<LoginResponse>;
  })

};

type LoginFormProps = {
  finish: () => void
}
export default function LoginForm(props: LoginFormProps) {

  const [errorMessage, setErrorMessage] = useState<string>();

  const auth = useAuth();
  const navigate = useNavigate()

  const onSuccess = (token: LoginResponse) => {
    setToken(token.access_token)
    API.Account.getUser()
      .then(user => {
        auth.login(user)
        navigate('/')
        props.finish()
      })
      .catch((error: Error) => {
        setErrorMessage(error.message)
      })
  }

  const onFailure = (error: any) => {
    if (error.message) {
      setErrorMessage(error.message)
    } else {
      try {
        error.json().then((data: any) => {
          const details = data.detail
          if (typeof details === 'string') {
            setErrorMessage(details)
          } else if (typeof details === 'object') {
            setErrorMessage(details[0]['msg'])
          } else {
            setErrorMessage('Unknown Error')
          }
        })
      } catch (e: any) {
        setErrorMessage('Unknown Error')
      }
    }
  }

  const onSubmit = (username: string, password: string) => {
    doLogin(username, password)
      .then(onSuccess)
      .catch(onFailure)
  }

  return   (
    <>
      <CredentialsForm submitLabel={ 'Login' } onSubmit={onSubmit}/>
      { errorMessage && <Text type="danger">{errorMessage}</Text> }
      { !errorMessage && <br/> }
      <Link to='/signup' onClick={props.finish} >
        New? Sign Up
      </Link>
    </>
  );

}
