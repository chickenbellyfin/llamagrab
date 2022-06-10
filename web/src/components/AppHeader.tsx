import Icon, { SettingFilled } from "@ant-design/icons";
import { Menu, Tooltip, Layout, Modal, Button, Space } from "antd";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { ReactComponent as logo } from '../../public/gen.svg'
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import LoginForm from './LoginForm'
import { useState } from "react";
import DiscordButton from "./DiscordButton";

const { Header } = Layout;

type AppHeaderProps = {
  showLogo: boolean
}
export default function AppHeader(props: AppHeaderProps) {

  const [isLoginVisible, setLoginVisible] = useState(false);
  const auth = useAuth()
  const breakpoint = useBreakpoint();
  const location = useLocation();
  const navigate = useNavigate();

  const showLogin = () => setLoginVisible(true);
  const hideLogin = () => setLoginVisible(false);


  return (
    <>
      <Header style={{
        padding: Boolean(breakpoint.md) ? undefined : '0 20px',
        background: 'none'
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

          { (auth.user || location.pathname !== '/') &&
            // Discord button is only shown in header if the user is not on the landing page
            <DiscordButton size='middle' responsive/>
          }

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