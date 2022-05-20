import { Col,List, Row, Spin, Typography } from 'antd';
import { API, RegionStatus, ServerStatus } from '../api';
import { useEffect, useRef, useState } from 'react';
import StatusIcon from './ServerStatusIcon';
import ServerName from './ServerName';

const { Title, Text } = Typography;

interface ServerStatusListItemProps {
  serverStatus: ServerStatus
}
function ServerStatusListItem({serverStatus}: ServerStatusListItemProps) {
  return (
    <List.Item key={`${serverStatus.id}`}>
      <span>
        <span style={{marginRight: '10px'}}><StatusIcon status={serverStatus.status}/></span>
        <ServerName status={serverStatus}/>
      </span>
    </List.Item>
  );
}

interface RegionStatusListProps {
    status: RegionStatus
  }

  function RegionStatusList(props: RegionStatusListProps) {
    return (
      <List
        split={false}
        style={{width: '300px', height: '100%', margin:'0px 10px', padding:'20px', background:'#0000001a'}}
        header={
          <Row align='middle'>
          <Col style={{alignItems: 'middle'}}>
            <span style={{fontSize: '20px', margin: '0px 10px 0px 0px'}}>
              <StatusIcon status={props.status.online} filled/>
            </span>
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
