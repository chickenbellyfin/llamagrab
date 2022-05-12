import { PoweroffOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, LinkOutlined, LockOutlined } from "@ant-design/icons"
import { List, Card, Divider, Descriptions, Badge, Popconfirm, message, Spin } from "antd"
import { useState } from "react"
import { Link } from "react-router-dom"
import { API, ServerStatus } from "../api"
import { useAuth } from "../auth"

type ServerListItemProps = {
  server: ServerStatus
  invalidate: () => void
}

export default function ServerListItem({ server, invalidate }: ServerListItemProps) {

  const auth = useAuth()
  const [actionInProgress, setActionInProgress] = useState(false)
  const isOwner = server.owner == auth.user?.username;

  const makeAction = (
    apiCall: (serverId: number) => Promise<any>,
    success: string,
    error: string,
    callback?: () => void) => {
    return async () => {
      setActionInProgress(true)
      try {
        await apiCall(server.id)
        message.success(success)
      } catch {
        message.error(error)
      } finally {
        setActionInProgress(false)
        invalidate()
        if (callback) {
          callback()
        }
      }
    }
  }

  const onDelete = makeAction(
    API.Server.deleteServer,
    `Deleted ${ server.name }`,
    `Error deleting ${ server.name }`,
    auth.refresh
  )

  const onStart = makeAction(
    API.Server.startServer,
    `Started ${ server.name }`,
    `Failed to start ${ server.name }`
  )

  const onStop = makeAction(
    API.Server.stopServer,
    `Stopped ${ server.name }`,
    `Failed to stop ${ server.name }`
  )

  const editAction = (
    <Link to={`/edit/${server.id}`}>
      <EditOutlined/> EDIT
    </Link>
  );

  const startAction = ( <div onClick={onStart}><PlayCircleOutlined/> START</div>)
  const stopAction = (<div onClick={onStop}><PoweroffOutlined/> STOP</div>);

  let deleteAction: JSX.Element = <></>;
  if (isOwner) {
    deleteAction = (
      <Popconfirm
        title={<span>Are you sure you want to delete <b>{server.name}</b>?</span>}
        onConfirm={onDelete}
        okText='Yes, Delete'
        >
          <div className='action-delete'><DeleteOutlined/> DELETE</div>
      </Popconfirm>
    );
  }

  const actions: { [key: string]: any[]} = {
    'running': [
      stopAction,
      editAction,
      deleteAction
    ],
    'stopped': [
      startAction,
      editAction,
      deleteAction
    ]
  }


  return (
    <List.Item>
      <Spin spinning={actionInProgress}>
      <Card bordered
        style={{
          width: '100%',
          ...!isOwner ? { borderColor: '#556474'} : {}
        }}
        actions={actions[server.status]}>

        <h3>
          <b>{ server.isPrivate && <LockOutlined/>} {server.name}</b><Divider type='vertical'/>
          <span style={{opacity: '80%'}}>{server.gameMode}</span>
          { !isOwner &&
            <span style={{opacity: '80%', float: 'right'}}><LinkOutlined />&nbsp;{server.owner}</span>
          }
        </h3>
        <Divider/>

        <Descriptions
          colon={false}
          layout='vertical'
          size='small'
          labelStyle={{opacity:'85%'}}>
          <Descriptions.Item label="Status">
            <Badge
              status={server.status === 'running' ? 'success' : 'error'}
              text={server.status}/>
          </Descriptions.Item>
          <Descriptions.Item label="Region">{server.regionName || 'not set'}</Descriptions.Item>
        </Descriptions>
      </Card>
      </Spin>
    </List.Item>
  )
}
