import Icon, { SettingFilled } from "@ant-design/icons";
import { Menu, Tooltip, Layout } from "antd";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import { ReactComponent as logo } from '../../public/gen.svg'

const { Header } = Layout;
export default function AppHeader() {

  const auth = useAuth()

  return (
    <>
    <Header style={{padding: '0px', background: 'none'}}>      
      <a href='/'>
        <h1 style={{display: 'inline', float:'left'}}>
          <Icon component={logo}/>
          &nbsp;Server Manager (alpha)
        </h1>
      </a>
    <Menu 
      style={{float: 'right'}}
      theme='dark'
      mode='horizontal'
      selectedKeys={[]}
      disabledOverflow>
    
      { auth.user &&
        <Menu.Item key='settings'>
          <Tooltip title='Settings'>
            <Link to='/settings'>
              <SettingFilled style={{fontSize: '18px'}} />
              <span style={{opacity: '65%'}}> {auth.user.username.toUpperCase()}</span>
            </Link>
          </Tooltip>
        </Menu.Item>
      }
    </Menu>
    </Header>
    </>
  );
}