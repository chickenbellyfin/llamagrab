
import { Link, Navigate, Route, Routes, useLocation, useNavigate} from 'react-router-dom'
import { Col, Layout, Menu, Row, Spin } from 'antd'
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import { ProtectedRoute, useAuth } from './auth'

import './App.less'
import EditServerPage from './pages/EditServerPage';
import NewServerPage from './pages/NewServerPage';
import SettingsPage from './pages/SettingsPage';
import AdminPage from './pages/AdminPage';
import SignupPage from './pages/SignupPage';
import AppHeader from './components/AppHeader';
import Icon, { DatabaseFilled, GlobalOutlined } from '@ant-design/icons';

import { ReactComponent as adminLogo } from '../public/admin.svg'

const { Header, Content, Sider } = Layout;

function App () {
  
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const sidebarVisible = Boolean(auth.user)

  // Show a loading screen on first load while we confirm login status
  // if the user is logged in, they will end up at the URL page
  // if not, ProtectedRoute will take them to the login screen
  if (auth.firstLoad) {
    return (
      <Spin>
        <div style={{width:'100%', height: '100vh'}}/>
      </Spin>
    );
  }
  
  return (
    <>
    <Layout style={{height: '100vh'}}>
      <Header style={{zIndex: 1, width: '100%', padding: '0px' }}>
        <AppHeader/>
      </Header>
      <Layout style={{height: '100%'}}>
        {sidebarVisible &&
          <Sider 
            breakpoint='md'
            collapsedWidth={0}
             style={{
               height: '100vh',
               position: 'sticky',
               zIndex: 2
            }}
          >
          <Menu theme="dark" selectedKeys={[location.pathname]} mode="inline">
              <Menu.Item key='/'>
              <Link to='/'><DatabaseFilled/>&nbsp;&nbsp;Servers</Link>
              </Menu.Item>

              
              <Menu.Item key="/regions" disabled>
                <Link to='/regions'><GlobalOutlined/>&nbsp;&nbsp;Regions</Link>
              </Menu.Item>

              {auth.permissions.isAdmin() &&
                <Menu.Item 
                  key="/admin"
                  onClick={() => navigate('/admin')}>
                  <Link to='/admin'><Icon style={{fontSize:'18px'}} component={adminLogo}/>&nbsp;&nbsp;Admin</Link>
                </Menu.Item>
              }
            </Menu>
          </Sider>
        }
        <Content style={{padding: '20px', overflowX: 'hidden'}}>
          <Row justify='center'><Col lg={24} xl={18} xxl={16}>
          <Routes>

            {/* Login & Signup pages disabled for logged in users, will redirect to '/' */}
            { !auth.user && <Route path='/login' element={<LoginPage/>}/>}
            { !auth.user && <Route path='/signup' element={<SignupPage/>}/>}
            
            {/* Logged in pages should be wrapped in <ProtectedRoute> so that logged out users
                get redirected to /login */}
            <Route path='/' element={<ProtectedRoute><HomePage/></ProtectedRoute>}/>
            <Route path='/edit/:serverId' element={<ProtectedRoute><EditServerPage/></ProtectedRoute>}/>
            <Route path='/new' element={<ProtectedRoute><NewServerPage/></ProtectedRoute>}/>
            <Route path='/admin' element={<ProtectedRoute><AdminPage/></ProtectedRoute>}/>
            <Route path='/settings' element={<ProtectedRoute><SettingsPage/></ProtectedRoute>}/>
            
            {/* Any paths not defined redirect to '/' */}
            <Route path='*' element={<Navigate replace to='/'/>}/>
          </Routes>
          </Col></Row>
        </Content>
      </Layout>
    </Layout>
    </>
  );
}

export default App;
