import { CheckCircleFilled, CheckCircleOutlined, LockOutlined } from '@ant-design/icons';
import { Col,List, Row, Spin, Tooltip, Typography } from 'antd';
import { API, RegionStatus } from '../api';
import { useEffect, useRef, useState } from 'react';

const { Title, Text } = Typography;

interface RegionStatusListProps {
    status: RegionStatus
  }

  function RegionStatusList(props: RegionStatusListProps) {
    return (
      <List
        split={false}
        style={{width: '300px', margin:'0px 10px', padding:'20px', background:'#0000001a'}}
        header={
          <Row align='middle'>
          <Col style={{alignItems: 'middle'}}>
            <span style={{fontSize: '20px', margin: '0px'}}>
              <CheckCircleFilled style={{marginRight:'10px', color: '#52c41a'}}/>
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
          <List.Item key={`${item.id}`}>
            <CheckCircleOutlined style={{marginRight:'10px', color: '#52c41a'}}/>
            {item.isPrivate && <Tooltip title='Private Server'><LockOutlined/></Tooltip>}&nbsp;
            {item.name}
          </List.Item>
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
