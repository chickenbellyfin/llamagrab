import { Button, Card, message, PageHeader, Spin } from "antd";
import { GameServerConfigForm } from "../components/edit_server_form/GameServerConfigForm";

import { useNavigate } from 'react-router-dom'
import { API, GameServerConfig, ServerSettings } from "../api";

import defaultConfig from '../../../common/default.json'
import { SaveOutlined } from "@ant-design/icons";
import { useState } from "react";
import { NewServerConfigForm } from "../components/edit_server_form/ServerConfigForm";
import { useAuth } from "../auth";
import ContentWrapper from "../components/ContentWrapper";

const defaultServerSettings: ServerSettings = {}

export default function NewServerPage() {

  const navigate = useNavigate()
  const auth = useAuth()
  const [config, setConfig] = useState<GameServerConfig>(defaultConfig)
  const [settings, setSettings] = useState<ServerSettings>(defaultServerSettings)

  const [isSaving, setIsSaving] = useState(false)

  const saveConfig = async () => {
    setIsSaving(true);
    try {
      if (config && settings) {
        await API.Server.createServer(config, settings)
      }
      message.success('Created New Server');
      navigate('/')
    } catch (error) {
      message.error('Failed to Create Server: ' + (error as Error).message);
    }
    setIsSaving(false)
    auth.refresh()
  }

  return (
    <ContentWrapper>
      <PageHeader
        title={'Create New Server'}
        onBack={() => navigate('/')}
        extra={[
          <Button
          type='primary'
          icon={<SaveOutlined/>}
          onClick={() => saveConfig()}
          loading={isSaving}>Save</Button>
        ]}/>
      <Spin spinning={isSaving}>
        <Card title='Server Settings' style={{marginBottom: '20px'}}>
          <NewServerConfigForm settings={defaultServerSettings} onChange={setSettings}/>
        </Card>
      </Spin>
      <Spin spinning={isSaving}>
        <Card title='Tribes Settings'>
        <GameServerConfigForm  config={defaultConfig} onChange={setConfig}/>
        </Card>
      </Spin>
    </ContentWrapper>
  )
}