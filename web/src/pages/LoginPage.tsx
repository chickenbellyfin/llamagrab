import { useState } from 'react';
import { BASE_URL } from '../config'
import { setToken, useAuth } from '../auth'
import { Typography, Card, Layout } from 'antd'
import { Navigate, useNavigate } from 'react-router';
import { API } from '../api';
import CredentialsForm from '../components/CredentialsForm';

const { Content } = Layout;
const { Text } = Typography;

type LoginResponse = {
  access_token: string,
  token_type: string,
}

async function doLogin(
  username: string,
  password: string,
  ): Promise<LoginResponse> {
  return fetch( BASE_URL + '/api/account/login', {
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

export default function LoginPage() {

  const [errorMessage, setErrorMessage] = useState<string>();

  const auth = useAuth();  
  const navigate = useNavigate()

  const onSuccess = (token: LoginResponse) => {
    setToken(token.access_token)
    API.Account.getUser()
      .then(user => {
        auth.login(user)
        navigate('/')
      })
      .catch((error: Error) => {
        setErrorMessage(error.message)
      })
  }

  const onFailure = (error: Response) => {
    error.json().then(data => {
      const details = data.detail
      if (typeof details === 'string') {
        setErrorMessage(details)
      } else if (typeof details === 'object') {
        setErrorMessage(details[0]['msg'])
      } else {
        setErrorMessage('Uknown Error')
      }
    })
  }

  const onSubmit = (username: string, password: string) => {
    doLogin(username, password)
      .then(onSuccess)
      .catch(onFailure)
  }

  if (auth.user) {
    return <Navigate to='/'/>
  } else {
    return   (
      <Card title='Login' style={{margin: '1em'}}>
        <Content>
          <CredentialsForm submitLabel={ 'Login' } onSubmit={onSubmit}/>
          { errorMessage && <Text type="danger">{errorMessage}</Text> }
          { !errorMessage && <br/> }
        </Content>
      </Card>
    );
  }
}
