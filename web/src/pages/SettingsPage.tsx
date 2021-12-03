import { LogoutOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, message, PageHeader, Row, Space, Typography } from "antd";
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

function ProfileForm() {

  const auth = useAuth()
  const [tribesUsername, setTribesUsername] = useState<string | undefined>(auth.user?.tribesUsername);
  const [errorMessage, setErrorMessage] = useState<string>();
  const [form] = Form.useForm()

  const onSubmit = () => {    
    if (tribesUsername) {
      API.Account.setTribesUsername(tribesUsername)
      .then(() => {
        form.resetFields()
        message.success("Updated");
      })
      .catch((error: Error) => {
        setErrorMessage(error.message);
      }).finally(() => {
        auth.refresh()
      })
    }
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
          label="Tribes Username"
          extra="Your username on the Tribes Ascend Community Servers (ta.kfk4ever.com). This is used to set up automatic admin access to servers"
          name="tribes_username"
          
          rules={[{ required: true, message: 'Required' }]}>
          <Input defaultValue={tribesUsername} onChange={(e) => setTribesUsername(e.target.value)}/>
        </Form.Item>

        <Form.Item wrapperCol={{ offset: 6, span: 14 }}>
          <Button type="primary" htmlType="submit">Update Profile</Button>
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
    <Card title="Tribes Username" style={{marginBottom: '10px'}}>
      <ProfileForm/>
    </Card>
    <Card title="Change Password">
      <ChangePasswordForm/>
    </Card>
  </>);
}