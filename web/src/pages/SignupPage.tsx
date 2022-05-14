import { Card, Layout, message, Typography} from "antd";
import { useState } from "react";
import { useNavigate } from "react-router";
import { API } from "../api";
import ContentWrapper from "../components/ContentWrapper";
import CredentialsForm from "../components/CredentialsForm";

const { Content } = Layout;
const { Text } = Typography;


export default function SignupPage() {

  const [errorMessage, setErrorMessage] = useState<string>();
  const navigate = useNavigate()

  const onSubmit = (username: string, password: string) => {
    API.Account.createUser({
      username, password
    })
    .then(() => {
      message.success('Account Created. Please login', 5)
      navigate('/login')
    })
    .catch((error: Error) => {
      setErrorMessage(error.message)
    })

  }

  return (
    <ContentWrapper>
      <Card title='Sign Up' style={{margin: '1em'}}>
        <Content>
          <CredentialsForm submitLabel={ 'Create Account' } onSubmit={onSubmit} signUp/>
          { errorMessage && <Text type="danger">{errorMessage}</Text> }
          { !errorMessage && <br/> }
        </Content>
      </Card>
    </ContentWrapper>
  );
}