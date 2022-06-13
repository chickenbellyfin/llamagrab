import { HistoryOutlined, RollbackOutlined, SaveOutlined } from "@ant-design/icons";
import { Button, Card, List, message, Modal, PageHeader, Popconfirm, Row, Spin, Tag } from "antd";
import { useState } from "react";
import { useNavigate, useParams } from 'react-router-dom';
import { API } from "../api";
import ContentWrapper from "../components/ContentWrapper";
import Loader from "../components/Loader";
import { GameServerConfig, ServerSettings, ServerStatus, ServerVersion, User } from "../domain";
import games from "../editor/games";
import ServerSettingsForm from "../editor/ServerSettingsForm";
import useLoader from "../useLoader";

const DATE_FORMAT: Intl.DateTimeFormatOptions = {
  weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric'
};

interface ServerVersionListProps {
  history: ServerVersion[]
  onRestoreVersion: (version: ServerVersion) => void
}
function ServerVersionList({ history, onRestoreVersion }: ServerVersionListProps) {
  return <List
    dataSource={history}
    style={{ overflow: 'auto', maxHeight: '500px' }}
    renderItem={item => {
      let changes = `${item.numChanges} Change${item.numChanges == 1 ? '' : 's'}`
      if (item.numChanges == -1) {
        changes = 'Created'
      }
      changes += ` by ${item.createdBy}`
      const dateString = new Date(item.createdAt * 1000).toLocaleDateString('en-US', DATE_FORMAT);
      const isCurrentVersion = item == history[0];

      let actions: any = [];
      if (!isCurrentVersion) {
        actions = [
          <Popconfirm
            title={<span>Are you sure you want to revert to <b>{dateString}</b>?</span>}
            okText='Yes, Revert'
            onConfirm={() => {
              onRestoreVersion(item)
            }}>
            <Button
              size='small'
            >
              <RollbackOutlined />Restore
            </Button>
          </Popconfirm>
        ]
      }

      return (
        <List.Item actions={actions}>
          <List.Item.Meta
            title={
              <>
                {changes}&nbsp;&nbsp;&nbsp;
                {isCurrentVersion &&
                  <Tag color='green'>Current Version</Tag>
                }
              </>
            }
            description={dateString} />
        </List.Item>
      );
    }}
  />;
}

interface ServerHistoryListLoaderProps {
  serverId: number,
  onRestoreVersion: (version: ServerVersion) => void
}
const ServerHistoryListLoader = Loader<ServerHistoryListLoaderProps, ServerVersion[]>({
  loaderFunc: (props) => API.Server.getServerVersions(props.serverId),
  componentBuilder: (serverHistory, props) => {
    serverHistory.sort((a, b) => b.createdAt - a.createdAt);
    return <ServerVersionList history={serverHistory} onRestoreVersion={props.onRestoreVersion} />
  }
});

interface EditorLoaderResult {
  settings: ServerSettings,
  config: GameServerConfig,
  regions: { [key: string]: string },
  users: User[],
  status: ServerStatus
}
async function loadServerEditor(serverId: number): Promise<EditorLoaderResult> {
  try {
    const settingsPromise = API.Server.getServerSettings(serverId)
    const configPromise = API.Server.getServerConfig(serverId)
    const status = API.Server.getServerStatus(serverId)
    const regions = API.Data.getRegions()
    const users = API.Account.getAllUsers()
    return {
      settings: await settingsPromise,
      config: await configPromise,
      regions: await regions,
      users: await users,
      status: await status
    }
  } catch (error: any) {
    throw Error('Failed to get settings')
  }
}

export default function EditServerPage() {

  const navigate = useNavigate()
  const { serverId } = useParams() as any
  const [config, setConfig] = useState<GameServerConfig>()
  const [settings, setSettings] = useState<ServerSettings>()
  const [isSaving, setIsSaving] = useState(false)
  const [isHistoryVisible, setHistoryVisible] = useState(false)
  const [historyRefreshKey, setHistoryRefreshKey] = useState(0)
  const [formRefreshKey, setFormRefreshKey] = useState(0)

  const loader = useLoader(() => loadServerEditor(serverId))

  const showHistory = () => {
    setHistoryRefreshKey(historyRefreshKey + 1)
    setHistoryVisible(true)
  }

  const hideHistory = () => {
    setHistoryVisible(false);
  }

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

  const revertToVersion = async (version: ServerVersion) => {
    setHistoryVisible(false)
    setIsSaving(true);
    await API.Server.setServerConfig(version.serverId, JSON.parse(version.serverConfig))
    setFormRefreshKey(formRefreshKey + 1)
    setIsSaving(false)
  }

  const isConfigChanged = Boolean(config) || Boolean(settings);
  const isValid = (
    settings?.region !== undefined
    && config?.displayName !== undefined
    && config.displayName.length != 0
  )

  const gameSpec = loader.value && games[loader.value?.settings.game];

  return (
    <ContentWrapper>
      <Modal
        visible={isHistoryVisible}
        footer={null}
        onCancel={hideHistory}
        title='Settings History'>
        <ServerHistoryListLoader key={`${historyRefreshKey}`} onRestoreVersion={revertToVersion} serverId={serverId} />
      </Modal>
      <PageHeader
        title={<span className="ui-title">{`Edit ${config?.displayName || 'Server'}`}</span>}
        onBack={() => navigate('/')}
        extra={[
          <Button
            key='history'
            icon={<HistoryOutlined />}
            onClick={showHistory}
            disabled={!loader.value}
            style={{ marginRight: '10px' }}>History</Button>,
          <Button
            key='save'
            type='primary'
            icon={<SaveOutlined />}
            onClick={() => saveConfig()}
            disabled={!isConfigChanged && !isValid}
            loading={isSaving}>Save</Button>
        ]} />
      <Row justify='end' style={{ marginBottom: '10px' }}>
      </Row>
      {loader.value && gameSpec ?
        <>
          <Spin spinning={isSaving}>
            <Card title='Server Settings' style={{ marginBottom: '20px' }}>
              <ServerSettingsForm
                key={`serverSettings${formRefreshKey}`}
                settings={loader.value.settings}
                regions={loader.value.regions}
                status={loader.value.status}
                users={loader.value.users}
                onChange={setSettings} />
            </Card>
          </Spin>
          <Spin spinning={isSaving}>
            <Card title={`${gameSpec.title} Settings`}>
              <gameSpec.editor
                key={`gameSettings${formRefreshKey}`}
                config={loader.value.config}
                onChange={setConfig}
              />
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