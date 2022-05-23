import { DeleteOutlined, CheckOutlined, CrownOutlined, VerticalAlignBottomOutlined } from "@ant-design/icons"
import { Card, Divider, Popconfirm, message, Spin, Descriptions, Tag } from "antd"
import { useState } from "react"
import { API, UserAccount } from "../api"
import { useAuth } from "../auth"
import colors from "../colors"

type UserAccountCardProps = {
  user: UserAccount
  invalidate: () => void
  onDelete: () => void
}

/**
 * Dialog for user control on the admin page
 * @param props
 * @returns
 */
export default function UserAccountCard(props: UserAccountCardProps) {

  const auth = useAuth()
  const [actionInProgress, setActionInProgress] = useState(false)

  const makeAction = (
    apiCall: (userId: number) => Promise<any>,
    callback?: () => void) => {
    return async () => {
      setActionInProgress(true)
      try {
        await apiCall(props.user.id)
        message.success(`Updated ${props.user.username}`)
      } catch (e) {
        message.error(`Failed to update ${props.user.username}: ${e}`)
      } finally {
        setActionInProgress(false)
        props.invalidate()
        if (callback) {
          callback()
        }
      }
    }
  }

  const verifyAction = <div onClick={makeAction(API.Admin.verifyUser)}><CheckOutlined /> VERIFY</div>;
  const makeAdminAction = <div onClick={makeAction(API.Admin.makeAdmin)}><CrownOutlined /> MAKE ADMIN</div>;
  const removeAdminAction = <div onClick={makeAction(API.Admin.removeAdmin)}><VerticalAlignBottomOutlined /> REMOVE ADMIN</div>;
  const deleteAction = (
    <Popconfirm
        title={<span>Are you sure you want to delete <b>{props.user.username}</b>?</span>}
        onConfirm={makeAction(API.Account.deleteUser, props.onDelete)}
        okText='Yes, Delete'>
      <div className='action-delete'><DeleteOutlined/> DELETE USER</div>
    </Popconfirm>
  );

  const actions = [
    ...auth.permissions.canVerifyUser(props.user) ? [verifyAction] : [],
    ...auth.permissions.canMakeAdmin(props.user) ? [makeAdminAction] : [],
    ...auth.permissions.canRemoveAdmin(props.user) ? [removeAdminAction] : [],
    ...auth.permissions.canDeleteUser(props.user) ? [deleteAction] : [],
  ];

  return (
      <Spin spinning={actionInProgress}>
        <Card bordered
          style={{
            backgroundColor: '#383e47',
            minWidth: '280px'
          }}
          actions={actions}>


          <h3>
            User: <b>{props.user.username}</b>
          </h3>
          <Divider/>
          <Descriptions
            colon={false}
            layout='vertical'
            size='small'
            labelStyle={{opacity:'85%'}}>
            <Descriptions.Item label="Tier">
              <Tag color={colors.tiers[props.user.tier]}>{props.user.tier.toUpperCase()}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Servers / Max">
              {`${props.user.limits.serverCount} / ${props.user.limits.serverLimit || '∞'}`}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Spin>
  )
}
