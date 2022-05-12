import { Button, message, PageHeader, Popconfirm, Space, Table, Tag, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import { API, ServerStatus, UserAccount, UserLimits } from "../api";
import Loader from "../components/Loader";
import { useAuth } from "../auth";
import ServerStatusLabel from "../components/ServerStatusLabel";
import { CaretRightFilled, CloseSquareOutlined, DeleteOutlined, LockOutlined } from "@ant-design/icons";
import { useState } from "react";

const tierColors: {[key: string]: any} = {
  'super': 'red',
  'admin': 'purple',
  'verified': 'green',
  'unverified': ''
}

type UserListProps = {
  users: Array<UserAccount>,
  invalidate: () => void,
  invalidateParent: () => void
}
function UserList ({ users, invalidate, invalidateParent }: UserListProps) {

  async function updateUser(
    user: UserAccount,
    action: (id: number) => void,
    invalidateFunc: () => void = invalidate
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
    { title: 'id', dataIndex:'id' },
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
    <Table<UserAccount> pagination={false} columns={columns} dataSource={users} size='small'/>
  );
}

interface UserListLoaderProps {invalidateParent: () => void}
const UserListLoader = Loader<UserListLoaderProps, UserAccount[]>({
  loaderFunc: API.Account.getAllUserAccounts,
  componentBuilder:(users, props, invalidate) => <UserList users={users} invalidate={invalidate} invalidateParent={props.invalidateParent}/>
});


type AllServersListProps = {
  serverList: Array<ServerStatus>
  invalidate: () => void,
  invalidateParent: () => void
}

function AllServersList({serverList, invalidate, invalidateParent}: AllServersListProps) {

  const [inProgress, setInProgress] = useState(false);
  const auth = useAuth()

  const doAction = async (
    serverId: number,
    apiCall: (serverId: number ) => Promise<any>,
    success: string,
    error: string,
    invalidateFunc: () => void = invalidate) => {
    setInProgress(true)
    try {
      await apiCall(serverId)
      message.success(success)
    } catch {
      message.error(error)
    } finally {
      setInProgress(false)
      invalidateFunc()
    }
  }

  const onStart = (server: ServerStatus) => doAction(
    server.id, API.Server.startServer, `Started ${server.name}`, `Failed to start ${server.name}`)
  const onStop = (server: ServerStatus) => doAction(
    server.id, API.Server.stopServer, `Stopped ${server.name}`, `Failed to stop ${server.name}`)
  const onDelete = (server: ServerStatus) => doAction(
    server.id, API.Server.deleteServer, `Deleted ${server.name}`, `Failed to delete ${server.name}`, invalidateParent)

  const serverColumns = [
    {title: 'id', dataIndex: 'id'},
    {title: () => <LockOutlined />, dataIndex: 'id', render: (id: number, server: ServerStatus) =>  <>{server.isPrivate && <LockOutlined />}</>},
    {title: 'Name', dataIndex: 'name'},
    {title: 'Status', dataIndex: 'status', render: (status: string) => <ServerStatusLabel status={status}/>},
    {title: 'Region', dataIndex: 'regionName'},
    {title: 'Owner', dataIndex: 'owner'},
    {
      title: 'Actions',
      dataIndex: 'id',
      render: (id: number, server: ServerStatus) => {
        return (
          <Space wrap>
            { server.status == 'running' &&
              <Button size='small' loading={inProgress} onClick={() => onStop(server)}><CloseSquareOutlined/> Stop</Button> }
            { server.status == 'stopped' &&
              <Button size='small' loading={inProgress} onClick={() => onStart(server)}><CaretRightFilled/> Start</Button> }
            { auth.permissions.canDeleteServer(server) &&
              <Popconfirm
                title={<span>Are you sure you want to delete <b>{server.name}</b>?</span>}
                onConfirm={() => onDelete(server)}
                okText='Yes, Delete'>
              <Button size='small' danger loading={inProgress}><DeleteOutlined /> Delete</Button>
            </Popconfirm> }
          </Space>
        );
      }
    }
  ]
  return (
    <Table<ServerStatus> pagination={false} columns={serverColumns} dataSource={serverList} size='small'/>
  );
}

interface ServerListLoaderProps { invalidateParent: () => void }
const ServerListLoader = Loader<ServerListLoaderProps, ServerStatus[]>({
  loaderFunc: API.Server.getAllServerList,
  componentBuilder:(servers, props, invalidate) => <AllServersList serverList={servers} invalidate={invalidate} invalidateParent={props.invalidateParent}/>
});

export default function AdminPage() {
  const [refreshKey, setRefresh] = useState(0);

  const refresh = () => setRefresh(refreshKey + 1)

  const navigate = useNavigate()
  return (
    <>
      <PageHeader title='Admin Panel' onBack={() => navigate('/')}/>
      <Typography.Title level={4}>User Management</Typography.Title>
      <UserListLoader key={`users${refreshKey}`} invalidateParent={refresh}/>
      <br/><br/>
      <Typography.Title level={4}>Server Management</Typography.Title>
      <ServerListLoader key={`servers${refreshKey}`} invalidateParent={refresh}/>
    </>
  );
}