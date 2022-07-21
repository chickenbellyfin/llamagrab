import { Modal, PageHeader, Spin, Table } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { Breakpoint } from "antd/lib/_util/responsiveObserve";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../../api";
import { useAuth } from "../../auth";
import ContentWrapper from "../../components/ContentWrapper";
import ServerCard from "../../components/ServerCard";
import ServerName from "../../components/ServerName";
import StatusIcon from "../../components/ServerStatusIcon";
import { ServerStatus, Status } from "../../domain";
import useLoader from "../../useLoader";

interface AllServersListProps {}
function AllServersList(props: AllServersListProps) {

  const loader = useLoader(API.Server.getAllServerList, [], 10)
  const [modalServerId, setModalServerId] = useState<number | undefined>();
  const breakpoint = useBreakpoint()
  const auth = useAuth();

  let modalServer = undefined;
  if (modalServerId !== undefined) {
    modalServer = loader.value?.find(s => s.id == modalServerId)
  }

  const serverColumns = [
    {title: 'id', dataIndex: 'id', responsive: ['md' as Breakpoint]},
    {
      title: 'Name',
      dataIndex: 'name',
      render: (name: string, item: ServerStatus) => <ServerName status={item}/>},
    {title: 'Status', dataIndex: 'status', render: (status: Status) => <StatusIcon status={status} showLabel={breakpoint.lg}/>},
    {title: 'Region', dataIndex: 'regionName'},
    {title: 'Owner', dataIndex: 'owner'}
  ]
  return (
    <Spin spinning={loader.initialLoad}>
      <Table<ServerStatus>
        rowKey='id'
        pagination={false}
        columns={serverColumns}
        dataSource={loader.value}
        size='small'
        onRow={(record, rowIndex) => {
          return {
            onClick: () => {
              setModalServerId(
                (rowIndex !== undefined && loader.value !== undefined) ?
                  loader.value[rowIndex].id : undefined)
            }
          };
        }}
      />
      {modalServer &&
        <Modal
          visible={modalServer !== undefined}
          onCancel={() => setModalServerId(undefined)}
          title={null}
          footer={null}
          bodyStyle={{
            padding: '0px'
          }}
        >
          <ServerCard
            server={modalServer} invalidate={loader.invalidate}
            maxWidth='unset'
            showOwner
            warnBeforeEdit={(auth.user?.username == modalServer.owner) ? undefined : "Admins should only edit servers for emergencies."}
            hideShareStyles
          />
        </Modal>
    }
    </Spin>
  );
}

export default function AdminPage() {
  const navigate = useNavigate()

  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">Server Management</span>} onBack={() => navigate('/')}/>
      <AllServersList/>
    </ContentWrapper>
  );
}
