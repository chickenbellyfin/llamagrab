import { Button, Form, Input } from "antd";
import { ReactNode, useState } from "react";



type CredentialsFormProps = {
  submitLabel: ReactNode
  onSubmit: (username: string, password: string) => void
  disabled?: boolean
}

export default function CredentialsForm({ submitLabel, onSubmit, disabled }: CredentialsFormProps) {
  const [username, setUsername] = useState<string>();
  const [password, setPassword] = useState<string>();

  const handleSubmit = () => {
    if (username && password) {
      onSubmit(username, password)
    }
  }
  
  return (
    <Form labelCol={{span: 4}} wrapperCol={{span: 18}} onFinish={handleSubmit}>
      <Form.Item label="Username" name="username" rules={[{ required: true, message: 'Required' }]}>
        <Input onChange={(e) => setUsername(e.target.value)} disabled={disabled}/>
      </Form.Item>
      <Form.Item label="Password" name="password" rules={[{ required: true, message: 'Required' }]}>
        <Input.Password onChange={e => setPassword(e.target.value)} disabled={disabled}/>
      </Form.Item>
      <Form.Item wrapperCol={{ offset: 4, span: 18 }}>
        <Button type="primary" htmlType="submit" disabled={disabled}>{ submitLabel }</Button>
      </Form.Item>
    </Form>
  );

}