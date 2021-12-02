import { Button, Form, Input, Space } from "antd";
import { ReactNode, useState } from "react";
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link } from "react-router-dom";



type CredentialsFormProps = {
  submitLabel: ReactNode
  onSubmit: (username: string, password: string) => void
  disabled?: boolean
  signUp?: boolean
}

export default function CredentialsForm({ submitLabel, onSubmit, disabled, signUp }: CredentialsFormProps) {
  const [username, setUsername] = useState<string>();
  const [password, setPassword] = useState<string>();

  const handleSubmit = () => {
    if (username && password) {
      onSubmit(username, password)
    }
  }
  
  return (
    <Form  onFinish={handleSubmit} style={{maxWidth: '400px', margin: '0 auto'}}>
      <Form.Item name="username" rules={[{ required: true, message: 'Required' }]}>
        <Input 
          prefix={<UserOutlined style={{opacity: '40%'}}/>}
          onChange={(e) => setUsername(e.target.value)} 
          placeholder='Username'/>
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true, message: 'Required' }]}>
        <Input.Password
          prefix={<LockOutlined style={{opacity: '40%'}}/>}
          onChange={e => setPassword(e.target.value)} 
          placeholder='Password'/>
      </Form.Item>
      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          disabled={disabled}
          style={{width: '100%'}}>
            { submitLabel }
        </Button>
      </Form.Item>
      {!signUp &&
      <Link to='/signup' >
        New? Sign Up
      </Link>
      }
    </Form>
  );

}