import { Col, Row } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import React from "react";

interface ContentWrapperProps { }

export default function (props: React.PropsWithChildren<ContentWrapperProps>) {
  const breakpoint = useBreakpoint();
  const padding = breakpoint.sm ? '20px' : '16px'; // less padding on smallest layout
  return (
    <Row style={{ padding: padding }} justify='center'>
      <Col xs={24} sm={20}>
        <>{props.children}</>
      </Col>
    </Row>
  );
};