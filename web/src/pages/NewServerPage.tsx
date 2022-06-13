import { SaveOutlined } from "@ant-design/icons";
import { Button, Card, message, PageHeader, Select, Spin } from "antd";
import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import { API } from "../api";
import { useAuth } from "../auth";
import ContentWrapper from "../components/ContentWrapper";
import { GameServerConfig, GameType, ServerSettings, User } from "../domain";
import games from "../editor/games";
import ServerSettingsForm from "../editor/ServerSettingsForm";
import useLoader from "../useLoader";

const { Option } = Select;

interface EditorLoaderResult {
  users: User[]
  regions: { [key: string]: string },
}
async function loadServerEditor(): Promise<EditorLoaderResult> {
  try {
    const regions = API.Data.getRegions()
    const users = API.Account.getAllUsers()
    return {
      users: await users,
      regions: await regions
    }
  } catch (error: any) {
    throw Error('Failed to get settings')
  }
}

export default function NewServerPage() {

  const navigate = useNavigate()
  const auth = useAuth()
  const [settings, setSettings] = useState<ServerSettings>({game: 'tribes_ascend_ootb'})
  const [config, setConfig] = useState<GameServerConfig>(games['tribes_ascend_ootb'].defaultConfig)

  const [isSaving, setIsSaving] = useState(false)
  const loader = useLoader(loadServerEditor)

  const onSettingsChange = (newSettings: ServerSettings) => {
    setSettings(Object.assign({}, newSettings));
  }

  const onConfigChange = (newConfig: GameServerConfig) => {
    setConfig(Object.assign({}, newConfig));
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

  const isValid = (
    settings.region !== undefined
    && config.displayName !== undefined
    && config.displayName.length != 0
    )

  const gameSpec = games[settings.game];

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
      { loader.value ?
        <>
          <Spin spinning={isSaving}>
            <Card title='Server Settings' style={{marginBottom: '20px'}}>
              <ServerSettingsForm
                settings={settings}
                regions={loader.value.regions}
                users={loader.value.users}
                onChange={onSettingsChange}/>
            </Card>
          </Spin>
          <Spin spinning={isSaving}>
            <Card
              title={
                <>
                <span>{gameSpec.title} Settings</span>
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
            <gameSpec.editor config={gameSpec.defaultConfig} onChange={onConfigChange}/>
            </Card>
          </Spin>
        </>
        :
        <Spin
        spinning
        size='large'
        style={{ width: '100%', padding: '10%' }} />
      }

    </ContentWrapper>
  )
}