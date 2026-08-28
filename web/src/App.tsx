import { Layout, Menu, Spin } from 'antd';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { ProtectedRoute, useAuth } from './auth';
import HomePage from './pages/HomePage';

import Icon, { DatabaseFilled, GlobalOutlined } from '@ant-design/icons';
import './App.less';
import AppHeader from './components/AppHeader';
import EditServerPage from './pages/EditServerPage';
import NewServerPage from './pages/NewServerPage';
import SettingsPage from './pages/SettingsPage';
import SignupPage from './pages/SignupPage';

import { Footer } from 'antd/lib/layout/layout';
import { useState } from 'react';
import { ReactComponent as adminLogo } from '../public/admin.svg';
import AuditLogAdminPage from './pages/admin/AuditLogAdminPage';
import IPLogAdminPage from './pages/admin/IPLogAdminPage';
import ServersAdminPage from './pages/admin/ServersAdminPage';
import SiteAdminPage from './pages/admin/SiteAdminPage';
import UsersAdminPage from './pages/admin/UsersAdminPage';
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
                title: '', // disables tooltip on mobile
                children: [
                  {
                    key: '/admin/users',
                    label: 'Users',
                    title: '', // disables tooltip on mobile
                  },
                  {
                    key: '/admin/servers',
                    label: 'Servers',
                    title: '', // disables tooltip on mobile
                  },                 
                  {
                    key: '/admin/site',
                    label: 'Site',
                    title: '', // disables tooltip on mobile
                  },                
                  {
                    key: '/admin/iplogs',
                    label: 'IPs & Bans',
                    title: '', // disables tooltip on mobile
                  },
                  {
                    key: '/admin/audit',
                    label: 'Audit Log',
                    title: '', // disables tooltip on mobile
                  }, 
                ]
              }] : []
            ]}/>
          </Sider>
        }
        <Content
          style={{
            // minWidth here allows the collapsible side menu to 'move' content out of the way instead of squishing it
            minWidth: '360px',
            overflowX: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            scrollbarGutter: 'stable'
        }}>
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
            <Route path='/regions' element={<ProtectedRoute><RegionsPage/></ProtectedRoute>}/>
            <Route path='/settings' element={<ProtectedRoute><SettingsPage/></ProtectedRoute>}/>
            { auth.permissions.isAdmin() &&
              <>
              <Route path='/admin/users' element={<ProtectedRoute><UsersAdminPage/></ProtectedRoute>}/>
              <Route path='/admin/servers' element={<ProtectedRoute><ServersAdminPage/></ProtectedRoute>}/>
              <Route path='/admin/site' element={<ProtectedRoute><SiteAdminPage/></ProtectedRoute>}/>
              <Route path='/admin/audit' element={<ProtectedRoute><AuditLogAdminPage/></ProtectedRoute>}/>
              <Route path='/admin/iplogs' element={<ProtectedRoute><IPLogAdminPage/></ProtectedRoute>}/>
              </>
            }

            {/* Any paths not defined redirect to '/' */}
            <Route path='*' element={<Navigate replace to='/'/>}/>
          </Routes>
          </div>
          <Footer style={{display: 'flex', flexFlow: 'row wrap', justifyContent: 'center', alignItems: 'center', gap: '10px 15px', textAlign:'center', whiteSpace:'nowrap', opacity: .7}}>
            © 2021-{new Date().getFullYear()}
            <a href='https://discord.gg/dd8JgzJ' rel='noreferrer' style={{color:'unset', textDecoration: 'underline'}}>Ask a question</a>
            <a href='https://feedback.wilderzone.org/' rel='noreferrer' style={{color:'unset', textDecoration: 'underline'}}>Give feedback</a>
            <a href='https://ko-fi.com/wilderzone' rel='noreferrer' style={{color:'unset', textDecoration: 'underline'}}>Donate</a>
            <a href='https://github.com/chickenbellyfin/llamagrab' rel='noreferrer' style={{color:'unset', textDecoration: 'underline'}}>Source code</a>
            <a href='https://wilderzone.org/' rel='noreferrer' style={{color:'unset', textDecoration: 'underline'}}>Maintained by Wilderzone.org</a>
          </Footer>
        </Content>
      </Layout>
    </Layout>
    </>
  );
}

export default App;
