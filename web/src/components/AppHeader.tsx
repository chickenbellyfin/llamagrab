import Icon, { DatabaseFilled, SettingFilled } from "@ant-design/icons";
import { Menu, Tooltip, Layout } from "antd";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import { ReactComponent as logo } from '../../public/gen.svg'
import { ReactComponent as adminLogo } from '../../public/admin.svg'

const { Header } = Layout;
export default function AppHeader() {

  const auth = useAuth()

  return (
    <>
    <Header>

      
    <a href='/'><h1 style={{display: 'inline', float:'left'}}><Icon component={logo}/> Server Manager</h1></a>
{/*     
    { auth.user &&
      <span style={{float: 'right'}}>{auth.user.username}</span>
    } */}
    <Menu 
      style={{float: 'right'}}
      theme='dark'
      mode='horizontal'
      selectedKeys={[]}
      disabledOverflow>
       
      { auth.user &&
        <Menu.Item key='home'>
          <Tooltip title='Home'>
            <Link to='/'><DatabaseFilled style={{fontSize: '18px'}}/></Link>
          </Tooltip>
        </Menu.Item>
      }

      { auth.user?.role === 'admin' &&              
        <Menu.Item key='admin'>
          <Tooltip title='Admin'>
            <Link to='/admin'><Icon style={{fontSize:'18px'}} component={adminLogo}/></Link>
          </Tooltip>
        </Menu.Item>
      }
      
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
//<EyeFilled style={{fontSize: '18px'}}/>