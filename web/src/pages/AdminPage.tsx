import { CopyOutlined, InfoCircleOutlined, ReloadOutlined } from "@ant-design/icons";
import { Button, Card, Empty, Input, List, message, PageHeader, Space, Statistic, Table, Tag, Tooltip, Typography } from "antd";
import Item from "antd/lib/list/Item";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API, User, UserLimits } from "../api";
import Loader from "../components/Loader";
import { ColumnsType } from 'antd/es/table';
import { useAuth } from "../auth";

const tierColors: {[key: string]: any} = {
  'super': 'red',
  'admin': 'purple',
  'verified': 'green',
  'unverified': ''

}


type UserListProps = {
  users: Array<User>,
  invalidate: () => void
}

function UserList ({ users, invalidate }: UserListProps) {

  async function updateUser(user: User, action: (id: number) => void) {
    try {
      await action(user.id);
      message.success(`Updated ${user.username}`)
    } catch (e) {
      message.error(`Failed to update ${user.username}: ${e}`)    
    } finally {
      invalidate()
    }
  }

  const auth = useAuth();

  const columns = [
    { 
      title: 'id',
      dataIndex:'id'
    },
    {
      title: 'Name',
      dataIndex: 'username',
    },
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
      render: (id: number, user: User) => (
        <Space>
          {auth.permissions.canVerifyUser(user) && <Button size='small' onClick={() => updateUser(user, API.Admin.verifyUser)}>Verify</Button>}
          {auth.permissions.canMakeAdmin(user) && <Button size='small' onClick={() => updateUser(user, API.Admin.makeAdmin)}>Make Admin</Button>}
          {auth.permissions.canRemoveAdmin(user) && <Button size='small' onClick={() => updateUser(user, API.Admin.removeAdmin)}>Remove Admin</Button>}
          {/* TODO {auth.permissions.canResetPassword(user) && <Button size='small'>Reset Password</Button>} */}
          {auth.permissions.canDeleteUser(user) && <Button danger size='small'>Delete</Button>}
        </Space>
      )
    }
  ];

  return (
    <Table<User> pagination={false} columns={columns} dataSource={users}/>
  );
}

const UserListLoader = Loader({
  loaderFunc: API.Account.getAllUsers,
  componentBuilder:(users, props, invalidate) => <UserList users={users} invalidate={invalidate}/>
});


export default function AdminPage() {
  const navigate = useNavigate()  
  return (
    <>
      <PageHeader title='Admin Panel' onBack={() => navigate('/')}/>
      <Typography.Title level={4}>User Management</Typography.Title>
      <UserListLoader/>
    </>
  );
}