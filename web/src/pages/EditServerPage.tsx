import { Button, Card, List, message, Modal, PageHeader, Popconfirm, Row, Spin, Tag } from "antd";
import { EditGameServerConfigForm } from "../components/edit_server_form/GameServerConfigForm";
import { useNavigate, useParams } from 'react-router-dom'
import { API, GameServerConfig, ServerVersion, ServerSettings } from "../api";
import { useState } from "react";
import { HistoryOutlined, RollbackOutlined, SaveOutlined } from "@ant-design/icons";
import ServerConfigForm from "../components/edit_server_form/ServerConfigForm";
import Loader from "../components/Loader";

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
    style={{overflow: 'auto', maxHeight: '500px'}}
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
                { isCurrentVersion && 
                  <Tag color='green'>Current Version</Tag>
                }
              </>
            }
            description={dateString}/>
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
    return <ServerVersionList history={serverHistory} onRestoreVersion={props.onRestoreVersion}/>}
});

export default function EditServerPage() {

  const navigate = useNavigate()
  const { serverId } = useParams() as any
  const [config, setConfig] = useState<GameServerConfig>()
  const [settings, setSettings] = useState<ServerSettings>()
  const [isSaving, setIsSaving] = useState(false)
  const [isHistoryVisible, setHistoryVisible] = useState(false)
  const [historyRefreshKey, setHistoryRefreshKey] = useState(0)
  const [formRefreshKey, setFormRefreshKey] = useState(0)
  
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

  return (
    <>
      <Modal
        visible={isHistoryVisible}
        footer={null}
        onCancel={hideHistory}
        title='Settings History'>
          <ServerHistoryListLoader key={`${historyRefreshKey}`} onRestoreVersion={revertToVersion} serverId={serverId}/>
      </Modal>
      <PageHeader 
        title={`Edit ${config?.displayName || 'Server'}`}
        onBack={() => navigate('/')}/>
      <Row justify='end' style={{marginBottom: '10px'}}>
        <Button
          icon={<HistoryOutlined />}
          onClick={showHistory}
          style={{marginRight: '10px'}}>History</Button>
        <Button
          type='primary'
          icon={<SaveOutlined/>} 
          onClick={() => saveConfig()}
          disabled={!isConfigChanged}
          loading={isSaving}>Save</Button>
      </Row>
      <Spin spinning={isSaving}>
        <Card title='Server Settings' style={{marginBottom: '20px'}}>
          <ServerConfigForm key={`serverSettings${formRefreshKey}`} serverId={serverId} onChange={setSettings}/>
        </Card>
      </Spin>
      <Spin spinning={isSaving}>
        <Card title='Tribes Settings'>
          <EditGameServerConfigForm key={`gameSettings${formRefreshKey}`} serverId={serverId} onChange={setConfig}/>
        </Card>
      </Spin>
    </>
  )
}