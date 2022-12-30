import { PageHeader, Spin, Table, Tabs } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { useNavigate } from "react-router-dom";
import { API } from "../../api";
import ContentWrapper from "../../components/ContentWrapper";
import { AuditLogEvent } from "../../domain";
import useLoader from "../../useLoader";

const { TabPane } = Tabs

const DATE_FORMAT: Intl.DateTimeFormatOptions = {
  weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric', second: '2-digit'
};

const DATE_FORMAT_SHORT: Intl.DateTimeFormatOptions = {
  month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric',
};


function AuditLogList() {
  const breakpoint = useBreakpoint()
  const loader = useLoader(API.Admin.getAuditLog);
  const columns = [
    { 
      title: 'Timestamp',
      dataIndex: 'timestamp',
      render: (timestamp: number) => {
        return new Date(timestamp * 1000).toLocaleDateString('en-US', breakpoint.lg ? DATE_FORMAT: DATE_FORMAT_SHORT);
      }
    },
    { title: 'User', dataIndex: 'user_name'},
    { title: 'Details', dataIndex: 'details', render: (details: string) => <span style={{fontFamily: 'monospace'}}>{details}</span>}
  ];

  return (
    <>
      <Spin spinning={loader.initialLoad}>
        <Table<AuditLogEvent>
          rowKey='id'
          pagination={false}
          columns={columns}
          dataSource={loader.value}
          size='small'
          scroll={{x: true}}
          />
      </Spin>
    </>
  )

}

export default function AuditLogAdminPage() {
  const navigate = useNavigate()
  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">Audit Log</span>} onBack={() => navigate('/')}/>
      <AuditLogList/>
    </ContentWrapper>
  );
}
