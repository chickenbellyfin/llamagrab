import { Button, Form, Input } from "antd";
import { ReactNode, useState } from "react";
import { UserOutlined, LockOutlined } from '@ant-design/icons';


type CredentialsFormProps = {
  submitLabel: ReactNode
  onSubmit: (username: string, password: string) => void
  signUp?: boolean
  confirmPassword? : boolean
}

export default function CredentialsForm({ submitLabel, onSubmit, signUp, confirmPassword }: CredentialsFormProps) {
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
          prefix={<UserOutlined style={{opacity: '50%'}}/>}
          onChange={(e) => setUsername(e.target.value)}
          placeholder='Username'
          autoComplete="username"/>
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true, message: 'Required' }]}>
        <Input.Password
          prefix={<LockOutlined style={{opacity: '50%'}}/>}
          onChange={e => setPassword(e.target.value)}
          placeholder='Password'
          autoComplete={signUp ? 'new-password' : 'current-password'}/>
      </Form.Item>
      { confirmPassword &&
        <Form.Item name="confirm-password" rules={[
          {required: true, message: 'Required' },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue('password') === value) {
                return Promise.resolve();
              }
              return Promise.reject(new Error('Passwords must match'));
            },
          })
          ]}>
          <Input.Password
            prefix={<LockOutlined style={{opacity: '50%'}}/>}
            placeholder='Confirm Password'
            autoComplete={signUp ? 'new-password' : 'current-password'}/>
        </Form.Item>
      }
      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          style={{width: '100%'}}>
            { submitLabel }
        </Button>
      </Form.Item>
    </Form>
  );

}