import { Button, Card, message, PageHeader, Select, Spin } from "antd";

import { useNavigate } from 'react-router-dom'
import { API, GameServerConfig, GameType, ServerSettings } from "../api";

import { SaveOutlined } from "@ant-design/icons";
import { useState } from "react";
import { NewServerSettingsForm } from "../editor/ServerSettingsForm";
import { useAuth } from "../auth";
import ContentWrapper from "../components/ContentWrapper";
import games from "../editor/games";

const { Option } = Select;

export default function NewServerPage() {

  const navigate = useNavigate()
  const auth = useAuth()
  const [settings, setSettings] = useState<ServerSettings>({game: 'tribes_ascend_ootb'})
  const [config, setConfig] = useState<GameServerConfig>(games['tribes_ascend_ootb'].defaultConfig)

  const [isSaving, setIsSaving] = useState(false)


  const onSettingsChange = (newSettings: ServerSettings) => {
    setSettings(Object.assign({}, newSettings));
  }

  const onGameChange = (game: GameType) => {
    setSettings(Object.assign({}, settings, {game}))
    setConfig(games[game].defaultConfig)
  }

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

  const isValid = (settings.region !== undefined)

  const gameTitle = games[settings.game].title;
  const GameEditor = games[settings.game].editor
  const defaultGameConfig = games[settings.game].defaultConfig

  return (
    <ContentWrapper>
      <PageHeader
        title={<span className="ui-title">Create New Server</span>}
        onBack={() => navigate('/')}
        extra={[
          <Button
          key='save'
          disabled={!isValid}
          type='primary'
          icon={<SaveOutlined/>}
          onClick={() => saveConfig()}
          loading={isSaving}>Save</Button>
        ]}/>
      <Spin spinning={isSaving}>
        <Card title='Server Settings' style={{marginBottom: '20px'}}>
          <NewServerSettingsForm settings={settings} onChange={onSettingsChange}/>
        </Card>
      </Spin>
      <Spin spinning={isSaving}>
        <Card
          title={
            <>
            <span>{gameTitle} Settings</span>
            <Select
              style={{float: 'right'}}
              defaultValue="tribes_ascend_ootb"
              onChange={onGameChange}
              size='small'>
              <Option value="tribes_ascend_ootb">OOTB</Option>
              <Option value="tribes_ascend_goty">GOTY</Option>
            </Select>
            </>
          }>
         <GameEditor config={defaultGameConfig} onChange={setConfig}/>
        {/* <GameServerConfigForm  config={defaultConfig} onChange={setConfig}/> */}
        </Card>
      </Spin>
    </ContentWrapper>
  )
}