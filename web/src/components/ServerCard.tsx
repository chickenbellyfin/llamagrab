import { EditOutlined, LinkOutlined, PlayCircleOutlined, PoweroffOutlined, SyncOutlined } from "@ant-design/icons"
import { Card, Col, Descriptions, Divider, message, Popconfirm, Row, Spin, Tooltip } from "antd"
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
    error: string
  ) => {
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
      }
    }
  }

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

  const onRestart = makeAction(
    API.Server.restartServer,
    `Restarting ${ props.server.name }`,
    `Failed to restart ${ props.server.name }`
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

  const restartAction = (<div onClick={onRestart}><SyncOutlined/> RESTART</div>)

  const startAction = ( <div onClick={onStart}><PlayCircleOutlined/> START</div>)
  const stopAction = (<div onClick={onStop}><PoweroffOutlined/> STOP</div>);

  const actions = [
    ... props.server.enabled ? [stopAction] : [startAction],
    ... (props.server.enabled && props.server.status == 'running') ?[restartAction] : [],
    editAction
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

          <Row wrap={false}>
            <Col flex='auto'>
              <h3 className='no-overflow' style={{fontWeight: 700}}>
                <ServerName status={props.server}/>
              </h3>
            </Col>
            <Col flex='none' style={{marginLeft: '.5em'}}>
            { showAsShared &&
              <Tooltip title={`Shared by ${props.server.owner}`}>
                <span style={{opacity: '80%'}}>
                  <h3><LinkOutlined/></h3>
                </span>
              </Tooltip>
            }
            </Col>
          </Row>
          <Divider/>

          <Descriptions
            column={3}
            colon={false}
            layout='vertical'
            size='small'
            labelStyle={{opacity:'85%'}}>
            { props.showOwner &&
              <Descriptions.Item label="id">
                {props.server.id}
              </Descriptions.Item>
            }
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
