import { LogoutOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, message, PageHeader, Row, Typography } from "antd";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../api";
import { deleteToken, useAuth } from "../auth";


function ChangePasswordForm() {

  const [currentPassword, setCurrentPassword] = useState<string>("");
  const [newPassword, setNewPassword] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>();
  const [form] = Form.useForm()

  const onSubmit = () => {    
    API.Account.changePassword({
      currentPassword, newPassword
    })
    .then(() => {
      form.resetFields()
      message.success("Password Updated");
    })
    .catch((error: Error) => {
      setErrorMessage(error.message);
    })
  }

  return (
    <>
      <Form
        form={form}
        labelCol={{ span: 6 }}
        wrapperCol={{ span: 14 }}
        autoComplete="off"
        onFinish={onSubmit}>
        <Form.Item
          label="Current Password"
          name="password"
          rules={[{ required: true, message: 'Required' }]}>
          <Input.Password onChange={(e) => setCurrentPassword(e.target.value)}/>
        </Form.Item>

        <Form.Item
          label="New Password"
          name="new_password"
          rules={[{ required: true, message: 'Required' }]}>
          <Input.Password onChange={(e) => setNewPassword(e.target.value)}/>
        </Form.Item>

        <Form.Item wrapperCol={{ offset: 6, span: 14 }}>
          <Button type="primary" htmlType="submit">Change Password</Button>
        </Form.Item>
      </Form>
      { errorMessage && <Typography.Text type="danger">{errorMessage}</Typography.Text> }
      { !errorMessage && <br/> }
    </>
  );
}


export default function SettingsPage() {

  const navigate = useNavigate()
  const auth = useAuth()

  const onLogout = () => {
    deleteToken()
    auth.logout()
    navigate('/')
    //document.location.href = '/' // back to the home page
  }
  
  return (
  <>
  <PageHeader 
        title='Account Settings'
        onBack={() => navigate('/')}/>
  <Row style={{paddingBottom: '10px'}} justify='end'>
      <Button onClick={onLogout} size='large' danger><LogoutOutlined/> Log Out</Button>
  </Row>
  <Card title="Change Password">
    <ChangePasswordForm/>
  </Card>
  </>);
}