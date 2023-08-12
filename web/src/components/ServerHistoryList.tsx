import { RollbackOutlined } from "@ant-design/icons";
import { Button, Col, Collapse, Popconfirm, Row, Spin, Tag } from "antd";
import { useState } from "react";
import { API } from "../api";
import colors from "../colors";
import { ServerVersion, ServerVersionDetails } from "../domain";
import Loader from "./Loader";
import './ServerHistoryList.less';

const DATE_FORMAT: Intl.DateTimeFormatOptions = {
  weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric'
};

interface ServerVersionDetailsTableProps {
  details: ServerVersionDetails
}
function ServerVersionDetailsTable({ details }: ServerVersionDetailsTableProps) {

  const stringify = (value: string | any[], prefix: string) => {
    if (value === null) {
      return ""
    }
    if (Array.isArray(value)) {
      return (
        <>
          {(value as Array<any>).map(item => <>{prefix}&nbsp;{JSON.stringify(item)}<br/></>)}
        </>
      )
    } else {
      return <>{prefix} {JSON.stringify(value)}<br/></>
    }
  }

  return (
    <>
      {details.changes.length == 0 && "(no changes)"}
      {details.changes.map(change => {
        return (
          <>
            <h5>{change.field}</h5>
            <code >
              <span style={{color: colors.error.hex, overflowWrap: 'break-word'}}>{stringify(change.old, '-')}</span>
              <span style={{color: colors.success.hex, overflowWrap: 'break-word'}}>{stringify(change.new, '+')}</span>
            </code>
          </>
        )

      })}
    </>
  );
}

interface ServerVersionListProps {
  serverId: number,
  history: ServerVersion[]
  onRestoreVersion: (version: ServerVersion) => void
}
function ServerVersionList({ serverId, history, onRestoreVersion }: ServerVersionListProps) {
  const [versionDetails, setVersionDetails] = useState<{[k: number]: ServerVersionDetails}>({});

  const getVersionDetails = async (serverId: number, versionId: number) => {
    if (versionDetails[versionId] === undefined) {
      const details = await API.Server.getServerVersionDetails(serverId, versionId)
      setVersionDetails(Object.assign({}, versionDetails, {[versionId]: details}))
    }
  }

  return (
    <Collapse
      onChange={(keys) => {
        if (Array.isArray(keys) && keys.length > 0) {
          keys.forEach(key => getVersionDetails(serverId, parseInt(key)))
        }
      }}
      ghost>
      {history.map(item => {
        let changes = `${item.numChanges} Change${item.numChanges == 1 ? '' : 's'}`
        if (item.numChanges == -1) {
          changes = 'Created'
        }
        changes += ` by ${item.createdBy}`
        const dateString = new Date(item.createdAt * 1000).toLocaleDateString('en-US', DATE_FORMAT);
        const isCurrentVersion = item == history[0];
        return (
          <Collapse.Panel
            // collapsible={item.numChanges == -1 ? 'disabled': undefined}
            // styles from ant-list-item
            style={{borderBottom: '1px solid #22272d', padding: '12px'}}
            key={item.versionId}
            header={
              <Row style={{width: '100%'}}>
                <Col flex='auto'>
                  <h4 className="ant-list-item-meta-title">{changes}&nbsp;&nbsp;&nbsp;
                    {isCurrentVersion &&
                      <Tag color='green'>Current Version</Tag>
                    }
                  </h4>
                  <span className="ant-list-item-meta-description">{dateString}</span>
                </Col>
                <Col>
                  <Popconfirm
                    title={<span>Are you sure you want to revert to <b>{dateString}</b>?</span>}
                    okText='Yes, Revert'
                    onConfirm={() => {
                      onRestoreVersion(item)
                    }}>
                    <Button size='small' style={{top: '50%', transform: 'translateY(-50%)'}}>
                      <RollbackOutlined />Restore
                    </Button>
                  </Popconfirm>
                </Col>
              </Row>
            }>
            {versionDetails[item.versionId] ?
              <ServerVersionDetailsTable details={versionDetails[item.versionId]}/>
              :
              <Spin style={{width: '100%'}}/>
            }
          </Collapse.Panel>
        );
      })}
    </Collapse>
  )
}

interface ServerHistoryListLoaderProps {
  serverId: number,
  onRestoreVersion: (version: ServerVersion) => void
}

export default Loader<ServerHistoryListLoaderProps, ServerVersion[]>({
  loaderFunc: (props) => API.Server.getServerVersions(props.serverId),
  componentBuilder: (serverHistory, props) => {
    serverHistory.sort((a, b) => b.createdAt - a.createdAt);
    return <ServerVersionList serverId={props.serverId} history={serverHistory} onRestoreVersion={props.onRestoreVersion} />
  }
});
