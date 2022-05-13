import { Col, Row } from 'antd'

import ServerListItem from './ServerListItem'
import { API, ServerStatus } from '../api'
import Loader from './Loader'


type ServerListProps = {
  serverList: Array<ServerStatus>
  invalidate: () => void
}


export function ServerList({ serverList, invalidate }: ServerListProps) {
  return (
    <Row gutter={[16, 16]}>
      {
        serverList.map((item) => (
          <Col key={`${item.id}`}>
            <ServerListItem server={item} invalidate={invalidate}/>
          </Col>
        ))
      }
    </Row>
  )
}

export default Loader({
  loaderFunc: API.Server.getUserServerList,
  componentBuilder: ((result, props, invalidate) => <ServerList serverList={result} invalidate={invalidate}/>)
})
