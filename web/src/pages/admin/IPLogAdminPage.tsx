import { DeleteOutlined } from "@ant-design/icons";
import { Button, Card, Divider, Form, Input, message, PageHeader, Popconfirm, Spin, Table, Tabs, Typography } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { useNavigate } from "react-router-dom";
import { API } from "../../api";
import ContentWrapper from "../../components/ContentWrapper";
import { IPBan, IPLogEntry } from "../../domain";
import useLoader from "../../useLoader";

const { TabPane } = Tabs

const DATE_FORMAT: Intl.DateTimeFormatOptions = {
  weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', second: '2-digit'
};

const DATE_FORMAT_SHORT: Intl.DateTimeFormatOptions = {
  month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric',
};

const INSTRUCTIONS = (
  <>
    <h1>README</h1>
    This page allows us to block IPs or IP Ranges from gameservers. Adding/removing a rule here will apply to all servers within 10 seconds. There are some limitations compared to <code>/votekick</code>
    <ul>
      <li>This block only applies to servers on Llamagrab.</li>
      <li>The offender can still join the loginserver and send DMs to anyone.</li>
      <li>The offender may show up in the player list (but they will be unable to connect or play) </li>
    </ul>
    <h3>Range Bans</h3>
    Plain IP addresses (e.g. 1.2.3.4) will work, but it is recommended to ban an IP range when possible.
    <ol>
      <li>Look for most recent entry (top) for the offender in the "IP Logs" tab.</li>
      <li>Click on the "ARIN" link. On the new page, copy the CIDR. It will look something like:  1.2.3.4/16</li>
      <li>Paste it in this form as the IP. Please include in a note about who is banned and why.</li>
      <li>(Optional) Notify other admins in #admin</li>
    </ol>
    You may need to repeat these steps if the offender manages to change their IP. Leave the old bans in place if this happens.
  </>
);

function IPBansSection() {
  const loader = useLoader(API.Admin.getIPBans)
  const breakpoint = useBreakpoint()
  
  const [form] = Form.useForm()

  const onFinish = async (values: any) => {
    try {
      await API.Admin.createIPBan(values.ip, values.reason)
      form.resetFields()
      message.success('IP Ban Added')
    } catch (e) {
      message.error(`${e}`)
    } finally {
      loader.invalidate()
    }
  }

  const onDeleteBan = async (id: number) => {
    try {
      await API.Admin.removeIPBan(id)
      message.success('Removed Ban')
    } catch (e) {
      message.error(`${e}`)
    } finally {
      loader.invalidate()
    }
  }

  const columns = [
    {
      title: 'Date',
      dataIndex: 'created_at',
      render: (timestamp: number) => {
        return new Date(timestamp * 1000).toLocaleDateString('en-US', breakpoint.lg ? DATE_FORMAT: DATE_FORMAT_SHORT);
      }
    },
    {
      title: 'By',
      dataIndex: 'created_by'
    },
    {
      title: 'IP',
      dataIndex: 'ip'
    },
    {
      title: 'Reason',
      dataIndex: 'reason'
    },
    {
      title: '',
      dataIndex: 'id',
      render: (id: number) => {
        return (
        <Popconfirm title="Are you sure?" onConfirm={() => onDeleteBan(id)}>
          <Button size='small' danger icon={<DeleteOutlined/>}>{breakpoint.md && 'UNBAN'}</Button>
        </Popconfirm>)
      }
    }
  ]

  return (<>

    <Card style={{marginBottom: '10px'}} title="Create Ban">
      <Form  labelCol={{span: 4}} wrapperCol={{span: 16}} form={form} onFinish={onFinish}>
          {INSTRUCTIONS}
        <Divider></Divider>
        <Form.Item 
          name="ip" 
          label="IP/Network" 
          rules={[{
            required: true,
            pattern: /^([0-9]{1,3}\.){3}[0-9]{1,3}(\/[0-9]+)?$/
          }]}>
          <Input 
            placeholder="0.0.0.0[/0]"/>
        </Form.Item>
        <Form.Item name="reason" label="Reason" rules={[{ required: true }]}>
          <Input placeholder="Who? Why?"/>
        </Form.Item>
        <Form.Item wrapperCol={{ offset: 4, span: 16 }}>
          <Button type="primary" htmlType="submit">
            Ban!
          </Button>
        </Form.Item>
      </Form>
    </Card>
    
    <Spin spinning={loader.initialLoad}>
      <Table<IPBan>
        rowKey='id'
        pagination={false}
        columns={columns}
        dataSource={loader.value}
        size='small'
        />
    </Spin>
  </>)
}

function IPLogSection() {
  const breakpoint = useBreakpoint()
  const loader = useLoader(async () => {
    await API.Admin.fetchIPLogs()
    return await API.Admin.getIPLogs()
  }, []);

  const columns = [
    { 
      title: 'Last Seen',
      dataIndex: 'timestamp',
      render: (timestamp: number) => {
        return new Date(timestamp).toLocaleDateString('en-US', breakpoint.lg ? DATE_FORMAT: DATE_FORMAT_SHORT);
      }
    },
    {
      title: breakpoint.lg ? 'User ID' : 'UID',
      dataIndex: 'user_id',
      render: (user_id: number) => {
        if (user_id >= 1000000) {
          return `unvrf-${user_id-1000000}`
        } else {
          return user_id
        }
      }
    },
    {
      title: 'Username',
      dataIndex: 'display_name',
    },
    {
      title: 'IP/Geo',
      dataIndex: 'ip',
      render: (ip: string) => {
        return (
          <a href={`https://whatismyipaddress.com/ip/${ip}`} target="_blank">{ip}</a>
        );
      }
    },
    {
      title: 'ARIN',
      dataIndex: 'ip',
      render: (ip: string) => {
        return (
          <a href={`https://search.arin.net/rdap/?query=${ip}`} target="_blank">ARIN</a>
        );
      }
    },
    
    {
      title: breakpoint.lg? 'Server ID' : 'SID',
      dataIndex: 'label'
    }
  ];

  return (
    <>
      { loader.value &&
        <Typography.Text type="secondary">{loader.value?.length} Entries</Typography.Text>
      }

      <Spin spinning={loader.initialLoad}>
        <Table<IPLogEntry>
          rowKey='id'
          pagination={false}
          columns={columns}
          dataSource={loader.value}
          size='small'
          />
      </Spin>
    </>
  )

}

export default function IPLogAdminPage() {
  const navigate = useNavigate()

  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">Player IPs & Bans</span>} onBack={() => navigate('/')}/>

      <Tabs defaultActiveKey='log'>
        <TabPane tab="IP Logs" key='log'>
          <IPLogSection/>
        </TabPane>
        <TabPane tab="Bans" key='bans'>
          <IPBansSection/>
        </TabPane>
      </Tabs>

      
    </ContentWrapper>
  );
}
