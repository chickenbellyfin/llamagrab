import { Col, Row, Space, Spin } from 'antd'

import ServerCard from './ServerCard'
import { API } from '../api'
import useLoader from '../useLoader'

export default function ServerList() {
  const loader = useLoader(API.Server.getUserServerList, undefined, 10);
  return (
    <Spin spinning={loader.initialLoad}>
      <Row gutter={[16, 16]}>
        {
          loader.value?.map((item) => (
            <Col key={`${item.id}`}>
              <ServerCard server={item} invalidate={loader.invalidate}/>
            </Col>
          ))
        }
        { loader.value != undefined && loader.value?.length === 0 &&
          <Col span={24} style={{textAlign: 'center', opacity:0.5}}>
          <Space direction='vertical'>
            <br/>
            <h1 style={{fontSize:'48px', marginBottom:'0'}}>Welcome!</h1>
            <h2>You don't have any servers.<br/> Click <b>Create Server</b> to get started.</h2>
          </Space>
          </Col>

        }
      </Row>
    </Spin>
  )
}
