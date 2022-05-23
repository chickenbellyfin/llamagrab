import Icon, { SettingFilled } from "@ant-design/icons";
import { Menu, Tooltip, Layout, Modal, Button } from "antd";
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

        <Menu
          style={{ float: 'right' }}
          theme='dark'
          mode='horizontal'
          selectedKeys={[]}
          disabledOverflow>
         { (auth.user || location.pathname !== '/') && <DiscordButton size='middle' responsive/>}
          {auth.user &&
            <Menu.Item key='settings'>
              <Tooltip title='Settings'>
                <Link to='/settings'>
                  <SettingFilled style={{ fontSize: '18px' }} />
                  <span style={{ opacity: '65%' }}> {breakpoint.md && auth.user.username.toUpperCase()}</span>
                </Link>
              </Tooltip>
            </Menu.Item>
          }
          {
            !auth.user &&
            <Menu.Item key='login' onClick={showLogin}>
              LOG IN
            </Menu.Item>
          }
        </Menu>
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