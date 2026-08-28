import Icon, { SettingFilled } from "@ant-design/icons";
import { Button, Layout, Modal, Space, Tooltip } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ReactComponent as logo } from '../../public/gen.svg';
import { useAuth } from "../auth";
import LoginForm from './LoginForm';

const { Header } = Layout;

type AppHeaderProps = {
  showLogo: boolean
}
export default function AppHeader(props: AppHeaderProps) {

  const [isLoginVisible, setLoginVisible] = useState(false);
  const auth = useAuth()
  const breakpoint = useBreakpoint();
  const navigate = useNavigate();

  const showLogin = () => setLoginVisible(true);
  const hideLogin = () => setLoginVisible(false);


  return (
    <>
      <Header style={{
        padding: Boolean(breakpoint.md) ? undefined : '0 20px',
      }}>
        {props.showLogo &&
          <a href='/'>
            <h1 style={{ display: 'inline', float: 'left' }}>
              <Icon component={logo} />
              &nbsp;<span style={{ letterSpacing: '1.9px' }}>LLAMAGRAB</span>
            </h1>
          </a>
        }

        <Space direction="horizontal" size='middle' style={{float:'right'}}>

          {auth.user &&
            // user settings only shown if user is logged in
            <Tooltip title='Settings'>
              <Button type='text' onClick={() => navigate('/settings')}>
                <span style={{opacity: '.7'}}><SettingFilled/> {breakpoint.md && auth.user.username.toUpperCase()}</span>
              </Button>
            </Tooltip>
          }

          { !auth.user &&
            // login button only shown if user is not logged in
            <Button type='text' onClick={showLogin}>LOG IN</Button>
          }
        </Space>

        <Modal
          title="Login"
          visible={isLoginVisible}
          footer={null}
          onOk={hideLogin}
          onCancel={hideLogin}>
          <LoginForm finish={hideLogin} />
        </Modal>
      </Header>
    </>
  );
}