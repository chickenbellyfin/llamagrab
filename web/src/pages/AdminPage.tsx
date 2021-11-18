import { CopyOutlined, InfoCircleOutlined, ReloadOutlined } from "@ant-design/icons";
import { Button, Card, Input, message, PageHeader, Tooltip, Typography } from "antd";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../api";

type CreateInviteState = {
  inviteLink?: string,
  isLoading?: boolean
}

function CreateInvite() {

  const [state, setState] = useState<CreateInviteState>({
    isLoading: false
  })

  const getToken = () => {
    setState({isLoading: true});

    API.Admin.createInvite()
      .then(inviteToken => {
        const inviteLink = `${window.location.origin}/signup?invite_token=${inviteToken.invite_token}`
        setState({inviteLink: inviteLink, isLoading: false})
      })
      .catch(() => {message.error('Failed to create invite.')})
  }
  
  return (
    <>
    <Input.Group>
    <Input
      value={state.inviteLink}
      style={{ width: 'calc(100% - 100px)' }}/>
    {state.isLoading &&
        <Button icon={<ReloadOutlined spin/>}/>
    }
    {!state.inviteLink &&
      <Tooltip title="Generate New Invite">
        <Button icon={<ReloadOutlined />} onClick={getToken}/>
      </Tooltip>
    }
    {state.inviteLink &&
      <Tooltip title="Copy Invite Link">
        <Button 
          icon={<CopyOutlined />}
          onClick={() => state.inviteLink && navigator.clipboard.writeText(state.inviteLink)} />
      </Tooltip>
    }
  </Input.Group>
  <div style={{paddingTop:'5px'}}><Typography.Text type="secondary"><InfoCircleOutlined/> Invite links expire after 24 Hours</Typography.Text></div>
  </>
  
  );
}

export default function AdminPage() {

  const navigate = useNavigate()
  
  return (
    <>
      <PageHeader title='Admin Panel' onBack={() => navigate('/')}/>
      <Card title="Create Invite Link"><CreateInvite/></Card>
    </>
  );
}