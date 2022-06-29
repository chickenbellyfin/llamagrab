import { Layout, Menu, Spin } from 'antd';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { ProtectedRoute, useAuth } from './auth';
import HomePage from './pages/HomePage';

import Icon, { DatabaseFilled, GlobalOutlined } from '@ant-design/icons';
import './App.less';
import AppHeader from './components/AppHeader';
import AdminPage from './pages/AdminPage';
import EditServerPage from './pages/EditServerPage';
import NewServerPage from './pages/NewServerPage';
import SettingsPage from './pages/SettingsPage';
import SignupPage from './pages/SignupPage';

import { Footer } from 'antd/lib/layout/layout';
import { useState } from 'react';
import { ReactComponent as adminLogo } from '../public/admin.svg';
import LandingPage from './pages/LandingPage';
import RegionsPage from './pages/RegionsPage';

const { Header, Content, Sider } = Layout;

function App () {

  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isLanding = location.pathname === '/login';

  const sidebarVisible = Boolean(auth.user)
  const [isSidebarCollapsible, setSidebarCollapsible] = useState(false)
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false)
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
        <AppHeader showLogo={!isLanding}/>
      </Header>
      <Layout style={{height: '100%'}}>
        {sidebarVisible &&
          <Sider
            width={240}
            breakpoint='md'
            collapsed={isSidebarCollapsed}
            collapsedWidth={0}
            // track the sidebar collapse state so we can auto-close on click in mobile layouts
            onCollapse={(collapsed, type) => setSidebarCollapsed(collapsed)}
            onBreakpoint={(broken) =>  setSidebarCollapsible(broken)}
            style={{
              height: '100vh',
              position: 'sticky',
              zIndex: 2,
            }}
          >
          <Menu
            theme="dark"
            selectedKeys={[location.pathname]}
            mode="inline"
            onClick={(e) => {
              if (isSidebarCollapsible) {
                setSidebarCollapsed(true)
              }
              navigate(e.key)
            }}
            items={[
              {
                key: '/',
                icon: <DatabaseFilled/>,
                label: 'Servers',
                title: '', // disables tooltip on mobile
              },
              {
                key: '/regions',
                icon: <GlobalOutlined/>,
                label: 'Regions',
                title: '' // disables tooltip on mobile
              },
              ... auth.permissions.isAdmin() ? [{
                key: '/admin',
                icon: <Icon style={{fontSize:'18px'}} component={adminLogo}/>,
                label: 'Admin',
                title: '' // disables tooltip on mobile
              }] : []
            ]}/>
          </Sider>
        }
        <Content style={{
          // minWidth here allows the collapsible side menu to 'move' content out of the way instead of squishing it
          minWidth: '375px', overflowX: 'hidden', display: 'flex', flexDirection: 'column'}}>
          <div style={{flexGrow: 1 /* Forces content to expand vertically so footer is at the bottom*/}}>
          <Routes>

            {/* Login & Signup pages disabled for logged in users, will redirect to '/' */}
            { !auth.user && <Route path='/signup' element={<SignupPage/>}/>}

            {/* Logged in pages should be wrapped in <ProtectedRoute> so that logged out users
                get redirected to /login */}
            <Route path='/' element={
              auth.user ?
              <ProtectedRoute><HomePage/></ProtectedRoute>
              :
              <LandingPage/>
            }/>
            <Route path='/edit/:serverId' element={<ProtectedRoute><EditServerPage/></ProtectedRoute>}/>
            <Route path='/new' element={<ProtectedRoute><NewServerPage/></ProtectedRoute>}/>
            <Route path='/admin' element={<ProtectedRoute><AdminPage/></ProtectedRoute>}/>
            <Route path='/regions' element={<ProtectedRoute><RegionsPage/></ProtectedRoute>}/>
            <Route path='/settings' element={<ProtectedRoute><SettingsPage/></ProtectedRoute>}/>

            {/* Any paths not defined redirect to '/' */}
            <Route path='*' element={<Navigate replace to='/'/>}/>
          </Routes>
          </div>
          <Footer style={{textAlign:'center', whiteSpace:'nowrap', opacity: .7}}>
            © 2021-{new Date().getFullYear()} <a href='mailto:admin@llamagrab.net' style={{color:'unset', textDecoration: 'underline'}}>admin@llamagrab.net</a>
          </Footer>
        </Content>
      </Layout>
    </Layout>
    </>
  );
}

export default App;
