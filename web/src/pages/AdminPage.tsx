import { Button, message, Modal, PageHeader, Popconfirm, Space, Spin, Table, Tag, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import { API, ServerStatus, Status, UserAccount, UserLimits } from "../api";
import { useAuth } from "../auth";
import { useState } from "react";
import ContentWrapper from "../components/ContentWrapper";
import StatusIcon from "../components/ServerStatusIcon";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import ServerName from "../components/ServerName";
import useLoader from "../useLoader";
import ServerListItem from "../components/ServerCard";
import { Breakpoint } from "antd/lib/_util/responsiveObserve";

const tierColors: {[key: string]: any} = {
  'super': 'red',
  'admin': 'purple',
  'verified': 'green',
  'unverified': ''
}

type UserListProps = {
  invalidateParent: () => void
}
function UserList ({ invalidateParent }: UserListProps) {
  const loader = useLoader(API.Account.getAllUserAccounts, []);
  async function updateUser(
    user: UserAccount,
    action: (id: number) => void,
    invalidateFunc: () => void = loader.invalidate
  ): Promise<any> {
    try {
      await action(user.id);
      message.success(`Updated ${user.username}`)
    } catch (e) {
      message.error(`Failed to update ${user.username}: ${e}`)
    } finally {
      invalidateFunc()
    }
  }

  const auth = useAuth();

  const columns = [
    { title: 'id', dataIndex:'id', responsive: ['md' as Breakpoint] },
    { title: 'Name', dataIndex: 'username'},
    {
      title: 'Tier',
      dataIndex: 'tier',
      render: (tier: string) => <Tag color={tierColors[tier]}>{tier.toUpperCase()}</Tag>
    },
    {
      title: 'Servers / Max',
      dataIndex: 'limits',
      render: (limits: UserLimits) => {
        return (
        <>
        {`${limits.serverCount} / ${limits.serverLimit || '∞'}`}
        </>)
      }
    },
    {
      title: 'Actions',
      dataIndex: 'id',
      render: (id: number, user: UserAccount) => (
        <Space>
          {auth.permissions.canVerifyUser(user) && <Button size='small' onClick={() => updateUser(user, API.Admin.verifyUser)}>Verify</Button>}
          {auth.permissions.canMakeAdmin(user) && <Button size='small' onClick={() => updateUser(user, API.Admin.makeAdmin)}>Make Admin</Button>}
          {auth.permissions.canRemoveAdmin(user) && <Button size='small' onClick={() => updateUser(user, API.Admin.removeAdmin)}>Remove Admin</Button>}
          {/* TODO {auth.permissions.canResetPassword(user) && <Button size='small'>Reset Password</Button>} */}
          {auth.permissions.canDeleteUser(user) &&
            <Popconfirm
              title={<span>Are you sure you want to delete <b>{user.username}</b>?</span>}
              onConfirm={() => updateUser(user, API.Account.deleteUser, invalidateParent)}
              okText='Yes, Delete'>
              <Button danger size='small'>Delete</Button>
            </Popconfirm>
          }
        </Space>
      )
    }
  ];

  return (
    <Spin spinning={loader.initialLoad}>
      <Table<UserAccount> rowKey='id' pagination={false} columns={columns} dataSource={loader.value} size='small'/>
    </Spin>
  );
}

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
    {title: 'Name', dataIndex: 'name', render: (name: string, item: ServerStatus) => <ServerName status={item}/>},
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
          <ServerListItem
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
  const [refreshKey, setRefresh] = useState(0);
  const navigate = useNavigate()

  const refresh = () => setRefresh(refreshKey + 1)
  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">Admin Panel</span>} onBack={() => navigate('/')}/>
      <Typography.Title level={4}>User Management</Typography.Title>
      <UserList key={`users${refreshKey}`} invalidateParent={refresh}/>
      <br/><br/>
      <Typography.Title level={4}>Server Management</Typography.Title>
      <AllServersList key={`servers${refreshKey}`}/>
      <br/>
    </ContentWrapper>
  );
}