
import { Navigate, Route, Routes} from 'react-router-dom'
import { Col, Layout, Row } from 'antd'
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


const { Content } = Layout;


function App () {
  
  const auth = useAuth();
  
  return (
    <Layout style={{height: '100%'}}>
      <AppHeader/>
      <Content style={{padding: '20px'}}>
        <Row justify='center'><Col span={18} style={{maxWidth:'1200px'}}>
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
  );
}

export default App;
