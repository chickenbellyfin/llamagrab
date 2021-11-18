

  import { Alert, Card, Layout, message, Typography} from "antd";
  import { useState } from "react";
import { useNavigate } from "react-router";
import { API } from "../api";
  import CredentialsForm from "../components/CredentialsForm";
  
  const { Content } = Layout;
  const { Text } = Typography;


export default function SignupPage() {
  
  const [errorMessage, setErrorMessage] = useState<string>();
  const navigate = useNavigate()
  const urlSearchParams = new URLSearchParams(window.location.search);
  const inviteToken = urlSearchParams.get('invite_token')

  const onSubmit = (username: string, password: string) => {
    if (inviteToken) { 
      API.Account.createUser({
        username, password, inviteToken
      })
      .then(() => {
        message.success('Account Created. Please login', 5)
        navigate('/login')
      })
      .catch((error: Error) => {
        setErrorMessage(error.message)
      })
    }
  }

  return (
    <Card title='Sign Up' style={{margin: '1em'}}>
      <Content>
        {!inviteToken && 
          <>
          <Alert 
            message="Invite Link Required"
            description="Please contact an admin to get an invite link."
            type="warning" showIcon/>
          <br/>
          </>
        }
        <CredentialsForm submitLabel={ 'Create Account' } onSubmit={onSubmit} disabled={!Boolean(inviteToken)}/>
        { errorMessage && <Text type="danger">{errorMessage}</Text> }
        { !errorMessage && <br/> }
      </Content>
    </Card>
  );


}