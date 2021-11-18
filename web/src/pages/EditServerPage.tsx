import { Button, Card, message, PageHeader, Row, Spin } from "antd";
import { EditGameServerConfigForm } from "../components/edit_server_form/GameServerConfigForm";
import { useNavigate, useParams } from 'react-router-dom'
import { API, GameServerConfig, ServerSettings } from "../api";
import { useState } from "react";
import { SaveOutlined } from "@ant-design/icons";
import ServerConfigForm from "../components/edit_server_form/ServerConfigForm";

export default function EditServerPage() {

  const navigate = useNavigate()
  const { serverId } = useParams() as any
  const [config, setConfig] = useState<GameServerConfig>()
  const [settings, setSettings] = useState<ServerSettings>()
  const [isSaving, setIsSaving] = useState(false)
  
  const saveConfig = async () => {
    setIsSaving(true);
    try {
      if (config) {
        await API.Server.setServerConfig(serverId, config)
      }
      if (settings) {
        await API.Server.setServerSettings(serverId, settings);
      }
      message.success('Saved');
    } catch (error) {
      message.error('Error Saving Config: ' + (error as Error).message);
    }
    setIsSaving(false)
  }

  const isConfigChanged = Boolean(config) || Boolean(settings);

  return (
    <>
      <PageHeader 
        title={`Edit ${config?.displayName || 'Server'}`}
        onBack={() => navigate('/')}/>
      <Row justify='end' style={{marginBottom: '10px'}}>
        <Button
          type='primary'
          icon={<SaveOutlined/>} 
          onClick={() => saveConfig()}
          disabled={!isConfigChanged}
          loading={isSaving}>Save</Button>
      </Row>
      <Spin spinning={isSaving}>
        <Card title='Server Settings' style={{marginBottom: '20px'}}>
          <ServerConfigForm serverId={serverId} onChange={setSettings}/>
        </Card>
      </Spin>
      <Spin spinning={isSaving}>
        <Card title='Tribes Settings'>
          <EditGameServerConfigForm serverId={serverId} onChange={setConfig}/>
        </Card>
      </Spin>
    </>
  )
}