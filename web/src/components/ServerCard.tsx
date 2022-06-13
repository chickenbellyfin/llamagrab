import { PoweroffOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, LinkOutlined } from "@ant-design/icons"
import { Card, Divider, Descriptions, Popconfirm, message, Spin } from "antd"
import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { API } from "../api"
import { useAuth } from "../auth"
import { ServerStatus } from "../domain"
import games from "../editor/games"
import ServerName from "./ServerName"
import StatusIcon from "./ServerStatusIcon"

type ServerCardProps = {
  server: ServerStatus
  invalidate: () => void
  showOwner?: boolean
  warnBeforeEdit?: string
  maxWidth?: string
  minWidth?: string
  hideShareStyles?: boolean
}

export default function ServerCard(props: ServerCardProps) {

  const auth = useAuth()
  const [actionInProgress, setActionInProgress] = useState(false)
  const isOwner = props.server.owner == auth.user?.username;
  const navigate = useNavigate();

  const maxWidth = props.maxWidth === undefined ? '360px' : props.maxWidth
  const minWidth = props.minWidth === undefined ? '280px' : props.minWidth

  const showAsShared = !isOwner && !props.hideShareStyles;

  const makeAction = (
    apiCall: (serverId: number) => Promise<any>,
    success: string,
    error: string,
    callback?: () => void) => {
    return async () => {
      setActionInProgress(true)
      try {
        await apiCall(props.server.id)
        message.success(success)
      } catch {
        message.error(error)
      } finally {
        setActionInProgress(false)
        props.invalidate()
        if (callback) {
          callback()
        }
      }
    }
  }

  const onDelete = makeAction(
    API.Server.deleteServer,
    `Deleted ${ props.server.name }`,
    `Error deleting ${ props.server.name }`,
    auth.refresh
  )

  const onStart = makeAction(
    API.Server.startServer,
    `Started ${ props.server.name }`,
    `Failed to start ${ props.server.name }`
  )

  const onStop = makeAction(
    API.Server.stopServer,
    `Stopped ${ props.server.name }`,
    `Failed to stop ${ props.server.name }`
  )

  const editAction = props.warnBeforeEdit ?
    <Popconfirm
      title={<span>{props.warnBeforeEdit}</span>}
      onConfirm={() => navigate(`/edit/${props.server.id}`)}
      okText='Yes, Edit'><EditOutlined/> EDIT</Popconfirm>
    :
    <Link to={`/edit/${props.server.id}`}>
      <EditOutlined/> EDIT
    </Link>
    ;

  const startAction = ( <div onClick={onStart}><PlayCircleOutlined/> START</div>)
  const stopAction = (<div onClick={onStop}><PoweroffOutlined/> STOP</div>);

  let deleteAction: JSX.Element = <></>;
  if (!showAsShared) {
    deleteAction = (
      <Popconfirm
        title={<span>Are you sure you want to delete <b>{props.server.name}</b>?</span>}
        onConfirm={onDelete}
        okText='Yes, Delete'
        >
          <div className='action-delete'><DeleteOutlined/> DELETE</div>
      </Popconfirm>
    );
  }

  const actions = [
    ... props.server.enabled ? [stopAction] : [startAction],
    editAction,
    deleteAction
  ]

  return (
      <Spin spinning={actionInProgress}>
        <Card bordered
          style={{
            backgroundColor: '#383e47',
            maxWidth: maxWidth,
            minWidth: minWidth,
            ...showAsShared ? { borderColor: '#556474'} : {}
          }}
          actions={actions}>

          <h3>
            <b><ServerName status={props.server}/></b>
            { showAsShared &&
              <span style={{opacity: '80%', float: 'right'}}><LinkOutlined />&nbsp;{props.server.owner}</span>
            }
          </h3>
          <Divider/>

          <Descriptions
            colon={false}
            layout='vertical'
            size='small'
            labelStyle={{opacity:'85%'}}>
            <Descriptions.Item label="Status">
              <StatusIcon status={props.server.status} showLabel/>
            </Descriptions.Item>
            <Descriptions.Item label="Region">
              {props.server.regionName || 'not set'}
            </Descriptions.Item>
            <Descriptions.Item label="Game Type">
              {games[props.server.game].short}
            </Descriptions.Item>
            { props.showOwner &&
              <Descriptions.Item label="Owner">
                {props.server.owner}
              </Descriptions.Item>
            }
          </Descriptions>
        </Card>
      </Spin>
  )
}
