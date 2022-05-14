import { Button, PageHeader, Popover, Space } from 'antd'
import ServerList from '../components/ServerList';
import { PlusCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';
import ContentWrapper from '../components/ContentWrapper';

export default function HomePage() {

  const navigation = useNavigate();
  const auth = useAuth();

  let remainingServers = undefined;
  if (auth.user && auth.user.limits.serverLimit > 0) {

    remainingServers = Math.max(auth.user.limits.serverLimit - auth.user.limits.serverCount, 0);
  }

  let buttonComponent = (
    <Button
      size='large'
      type="primary"
      icon={<PlusCircleOutlined/>}
      style={{float: 'right', height: 'auto'}}
      disabled={remainingServers === 0}
      onClick={() => navigation('/new')}>
      {remainingServers === 0 ? '0 Remaining' : 'Create Server'}
    </Button>
  );

  if (remainingServers) {
    buttonComponent = (
      <Popover content={`${remainingServers} Remaining`} >
        { buttonComponent }
      </Popover>
    )
  }

  return (
    <ContentWrapper>
      <PageHeader
          title='Server List'
          extra={[buttonComponent]}/>
      <ServerList/>
    </ContentWrapper>
  );
};