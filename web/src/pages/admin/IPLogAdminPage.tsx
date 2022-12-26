import { CloudDownloadOutlined } from "@ant-design/icons";
import { Button, Card, PageHeader, Space, Spin, Table, Typography } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../../api";
import ContentWrapper from "../../components/ContentWrapper";
import { IPLogEntry } from "../../domain";
import useLoader from "../../useLoader";

const DATE_FORMAT: Intl.DateTimeFormatOptions = {
  weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', second: '2-digit'
};

const DATE_FORMAT_SHORT: Intl.DateTimeFormatOptions = {
  month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric',
};



export default function IPLogAdminPage() {
  const navigate = useNavigate()
  const breakpoint = useBreakpoint()
  const loader = useLoader(async () => {
    await API.Admin.fetchIPLogs()
    return await API.Admin.getIPLogs()
  }, []);
  const [isFetching, setIsFetching] = useState(false)

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
      title: 'IP',
      dataIndex: 'ip',
      render: (ip: string) => {
        return (
          <a href={`https://whatismyipaddress.com/ip/${ip}`} target="_blank">{ip}</a>
        );
      }
    },
    
    {
      title: breakpoint.lg? 'Server ID' : 'SID',
      dataIndex: 'label'
    }
  ];
  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">IP Logs</span>} onBack={() => navigate('/')}/>

      <Button
        style={{marginBottom: '10px'}}
        icon={<CloudDownloadOutlined/>}
        disabled={isFetching}
        onClick={async () => {
          setIsFetching(true)
          loader.invalidate()
          setIsFetching(false)
        }}>
        Fetch
      </Button> 

      &nbsp;{ loader.value &&
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
      
    </ContentWrapper>
  );
}
