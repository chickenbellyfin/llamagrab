import { Col, Row } from "antd";
import React from "react";

interface ContentWrapperProps {}
const ContentWrapper: React.FC = (props: React.PropsWithChildren<ContentWrapperProps>) => {
    return (
        <Row style={{padding: '20px'}} justify='center'>
            <Col xs={24} sm={20}>
                <>{props.children}</>
            </Col>
        </Row>
    );
}

export default ContentWrapper;