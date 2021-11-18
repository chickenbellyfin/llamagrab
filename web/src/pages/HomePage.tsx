import { Button, PageHeader, Popover, Space } from 'antd'
import ServerList from '../components/ServerList';
import { PlusCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';

type HomeProps = {
}

export default function HomePage(props: HomeProps) {

  const navigation = useNavigate();
  const auth = useAuth();

  let remainingServers = 0;
  if (auth.user) {
    remainingServers = Math.max(auth.user.serverLimit - auth.user.serverCount, 0);
  }

  return (
    <>
    <PageHeader 
        title='Server List'/>
      <Space direction='vertical' style={{width: '100%'}}>
        <Popover content={`${remainingServers} Remaining`}>
          <Button 
            size='large'
            type="primary"
            icon={<PlusCircleOutlined/>}
            style={{float: 'right', height: 'auto'}}
            disabled={remainingServers === 0}
            onClick={() => navigation('/new')}>
            Create Server
          </Button>
        </Popover>
        <ServerList/>
      </Space>
    </>
  );
};