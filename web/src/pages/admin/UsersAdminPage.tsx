import { Modal, PageHeader, Spin, Table, Tag } from "antd";
import { Breakpoint } from "antd/lib/_util/responsiveObserve";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../../api";
import colors from "../../colors";
import ContentWrapper from "../../components/ContentWrapper";
import UserAccountCard from "../../components/UserAccountCard";
import { UserAccount, UserLimits } from "../../domain";
import useLoader from "../../useLoader";

type UserListProps = {}
function UserList (props: UserListProps) {
  const loader = useLoader(API.Account.getAllUserAccounts, []);

  const [modalUserId, setModalUserId] = useState<number | undefined>();
  let modalUser = undefined;
  if (modalUserId !== undefined) {
    modalUser = loader.value?.find(u => u.id == modalUserId)
  }

  const columns = [
    { title: 'id', dataIndex:'id', responsive: ['md' as Breakpoint] },
    { title: 'Name', dataIndex: 'username'},
    {
      title: 'Tier',
      dataIndex: 'tier',
      render: (tier: string) => <Tag color={colors.tiers[tier]}>{tier.toUpperCase()}</Tag>
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
    }
  ];

  return (
    <Spin spinning={loader.initialLoad}>
      <Table<UserAccount>
        rowKey='id'
        pagination={false}
        columns={columns}
        dataSource={loader.value}
        size='small'
        onRow={(record, rowIndex) => {
          return {
            onClick: () => {
              setModalUserId(
                (rowIndex !== undefined && loader.value !== undefined) ?
                  loader.value[rowIndex].id : undefined)
            }
          };
        }}/>
      {modalUser &&
        <Modal
          visible={modalUser !== undefined}
          onCancel={() => setModalUserId(undefined)}
          title={null}
          footer={null}
          bodyStyle={{
            padding: '0px'
          }}
        >
          <UserAccountCard
            user={modalUser} invalidate={loader.invalidate} onDelete={loader.invalidate}
          />
        </Modal>
    }
    </Spin>
  );
}

export default function UsersAdminPage() {
  const navigate = useNavigate()

  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">User Management</span>} onBack={() => navigate('/')}/>
      <UserList/>
    </ContentWrapper>
  );
}
