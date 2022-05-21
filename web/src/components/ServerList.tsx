import { Col, Row, Spin } from 'antd'

import ServerListItem from './ServerListItem'
import { API } from '../api'
import useLoader from '../useLoader'

export default function ServerList() {
  const loader = useLoader(API.Server.getUserServerList, [], 60);
  return (
    <Spin spinning={loader.initialLoad}>
      <Row gutter={[16, 16]}>
        {
          loader.value?.map((item) => (
            <Col key={`${item.id}`}>
              <ServerListItem server={item} invalidate={loader.invalidate}/>
            </Col>
          ))
        }
      </Row>
    </Spin>
  )
}
