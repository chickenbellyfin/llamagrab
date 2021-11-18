import { Empty, List } from 'antd'

import ServerListItem from './ServerListItem'
import { API, ServerStatus } from '../api'
import Loader from './Loader'

type ServerListProps = {
  serverList: Array<ServerStatus>
  invalidate: () => void
}

export function ServerList({ serverList, invalidate }: ServerListProps) {
  return (
    <List 
      locale={{emptyText: (<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description='No Servers'/>)}}
      split={false}
      dataSource={serverList}
      renderItem={item => (<ServerListItem server={item} invalidate={invalidate}/>)}/>
  )
}

export default Loader({
  loaderFunc: API.Server.getServerList,
  componentBuilder: ((result, props, invalidate) => <ServerList serverList={result} invalidate={invalidate}/>)
})