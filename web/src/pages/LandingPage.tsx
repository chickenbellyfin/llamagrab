import { useAuth } from '../auth';
import { ReactComponent as logo } from '../../public/gen.svg'
import Icon, { CloudServerOutlined, ControlOutlined, CrownOutlined, SafetyCertificateOutlined, ThunderboltOutlined, UsergroupAddOutlined } from '@ant-design/icons';
import { Col, Divider, Row, Space, Typography } from 'antd';
import useBreakpoint from 'antd/lib/grid/hooks/useBreakpoint';

const { Title } = Typography;

type LandingPageProps = {
}

export default function LandingPage(props: LandingPageProps) {

  const auth = useAuth();
  const breakpoint = useBreakpoint();

  const content = [
    {
      icon: ThunderboltOutlined,
      text: "High Performance for Big Matches",
      short: "High Performance"
    },
    {
      icon: ControlOutlined,
      text: "100% Customizable. Community Maps Included",
      short: "100% Customizable"
    },
    {
      icon: CloudServerOutlined,
      text: "24/7 Cloud Hosting. Move Regions Instantly",
      short: "24/7 Cloud Hosting"
    },
    {
      icon: SafetyCertificateOutlined,
      text: "Secure Against Cheaters and Abuse",
      short: "Secure & Cheat-Free"
    },
    {
      icon: CrownOutlined,
      text: "Full Control With Automatic Admin Access",
      short: "Admin Access"
    },
    {
      icon: UsergroupAddOutlined,
      text: "Shared Editing & Admin Rights",
      short: "Shared Editing"
    },
  ];

  const titleStyle = {
    letterSpacing: '3.5px',
    marginTop: '0',
    marginBottom: '0',
    filter: 'drop-shadow(0px 0px 10px #1d84e366',
    opacity: '95%',
    lineHeight: '100%'
  };

  return (
    <>
      <div
        className='landing-logo'
        style={{
          textAlign:'center',
          padding: ' 10px 0px 40px 0px'
      }}>
        <Icon
          style={{
            color: '#1d84e3',
            fontSize:breakpoint.md ? '128px' : '96px',
            filter: 'drop-shadow(0px 0px 10px #1d84e355'
          }}
          component={logo}/>
        <Title style={titleStyle}>
          &nbsp;LLAMAGRAB
        </Title>
        <Title level={3} style={titleStyle}>
          SERVERS
        </Title>
      </div>
      <Divider
        style={{
          textAlign: 'center',
          opacity: '70%',
          fontWeight: 600,
          filter: 'drop-shadow(0px 0px 8px #ffffff22)',
          margin: '20px 0px 20px 0px'

        }}>
        TRIBES: ASCEND COMMUNITY SERVER HOSTING
      </Divider>
      <Row justify='center' gutter={[16, 16]} style={{padding: '0px 20px'}} wrap>
        { content.map(item =>
          <Col>

            <Space
              align='center'
              direction='vertical'
              style={{
                width: breakpoint.md? '280px': '100px',
                textAlign: 'center'
              }}>
              <item.icon
                    style={{
                    opacity: '80%',
                    padding: breakpoint.md ? '20px' : '0px 10px',
                    //color: '#73d13d',
                    filter: 'drop-shadow(0px 0px 8px #ffffff22)',
                    fontSize: breakpoint.md ? '48px': '48px'}}
                  />
              <Title level={5} style={{opacity: '85%', filter: 'drop-shadow(0px 0px 8px #ffffff22)'}}>
                {breakpoint.md? item.text : item.short}
              </Title>
            </Space>
          </Col>
          )
        }
      </Row>
    </>
  );
};