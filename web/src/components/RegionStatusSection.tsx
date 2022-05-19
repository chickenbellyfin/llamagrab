import { CheckCircleFilled, CheckCircleOutlined, ClockCircleOutlined, CloseCircleFilled, CloseCircleOutlined, LockOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { Col,List, Row, Spin, Tooltip, Typography } from 'antd';
import { API, RegionStatus, ServerStatus } from '../api';
import { useEffect, useRef, useState } from 'react';

const { Title, Text } = Typography;

interface ServerStatusListItemProps {
  serverStatus: ServerStatus
}
function ServerStatusListItem({serverStatus}: ServerStatusListItemProps) {
  let icon = <QuestionCircleOutlined style={{color: '#bfbfbf'}}/>
  let label = 'unknown status';
  switch(serverStatus.status) {
    case 'running':
      label = 'Running';
      icon = <CheckCircleOutlined style={{color: '#52c41a' }} />
      break;
    case 'starting':
      label = 'Starting';
      icon = <ClockCircleOutlined style={{color: '#faad14'}}/>;
      break;
    case 'stopping':
      label = 'Stopping';
      icon = <ClockCircleOutlined style={{color: '#faad14'}}/>;
      break;
    case 'offline':
      label = 'Offline';
      icon = <CloseCircleOutlined style={{color: '#ff4d4f'}}/>
  }

  return (
    <List.Item key={`${serverStatus.id}`}>
      <Tooltip title={label}>
        <span style={{marginRight: '10px'}}>{icon}</span>
      </Tooltip>
      {serverStatus.isPrivate && <Tooltip title='Private Server'><LockOutlined /></Tooltip>}&nbsp;
      {serverStatus.name}
    </List.Item>
  );
}

interface RegionStatusListProps {
    status: RegionStatus
  }

  function RegionStatusList(props: RegionStatusListProps) {

    let icon, label;
    if (props.status.online) {
      label = 'Online';
      icon = <CheckCircleFilled style={{color: '#52c41a'}}/>
    } else {
      label = 'Offline';
      icon = <CloseCircleFilled style={{color: '#ff4d4f'}}/>;
    }

    return (
      <List
        split={false}
        style={{width: '300px', height: '100%', margin:'0px 10px', padding:'20px', background:'#0000001a'}}
        header={
          <Row align='middle'>
          <Col style={{alignItems: 'middle'}}>
            <Tooltip title={label}>
              <span style={{fontSize: '20px', margin: '0px 10px 0px 0px'}}>
                {icon}
              </span>
            </Tooltip>
          </Col>
          <Col>
            <Title level={5} style={{margin: '0px', lineHeight: '100%'}}>{props.status.region}</Title>
            <Text type="secondary">REGION</Text>
          </Col>
          </Row>
        }
        dataSource={props.status.servers}
        renderItem={(item) =>
          <ServerStatusListItem serverStatus={item}/>
        }
        locale={{emptyText: 'No Active Servers'}}
      />
    );
  }

  export default function RegionStatusSection() {

    const [regionStatuses, setRegionStatuses] = useState<RegionStatus[] | null>(null);
    const timerRef = useRef<any>(null)

    const loadStatus = async () => {
      try {
        const statuses = await API.Server.getRegionStatus()
        setRegionStatuses(statuses)
        timerRef.current = setTimeout(loadStatus, 60000)
      } catch (e) {
        timerRef.current = setTimeout(loadStatus, 120000)
      }
    }

    useEffect(() => {
      loadStatus()
      return () => clearTimeout(timerRef.current);
    }, []);

    return (
      <Row justify='center' gutter={[16, 16]} style={{padding: '0px 20px'}} wrap>
        { regionStatuses !== null &&
          regionStatuses.map(item =>
            <Col key={item.region}><RegionStatusList status={item}/></Col>
          )
        }
        { regionStatuses == null &&
          <Col><Spin/></Col>
        }
      </Row>
    );
  }
