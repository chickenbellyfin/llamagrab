import { CloudDownloadOutlined, DeleteOutlined, SyncOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, message, PageHeader, Popconfirm, Space, Spin, Table, Tabs, Typography } from "antd";
import { useForm } from "antd/lib/form/Form";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API } from "../../api";
import ContentWrapper from "../../components/ContentWrapper";
import { AuditLogEvent, IPBan, IPLogEntry } from "../../domain";
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
  console.log(loader.value)
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
          />
      </Spin>
    </>
  )

}

export default function IPLogAdminPage() {
  const navigate = useNavigate()

  return (
    <ContentWrapper>
      <PageHeader title={<span className="ui-title">Audit Log</span>} onBack={() => navigate('/')}/>

      <AuditLogList/>
    </ContentWrapper>
  );
}
