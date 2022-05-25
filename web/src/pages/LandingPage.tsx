import { ReactComponent as logo } from '../../public/gen.svg'
import Icon, { CloudServerOutlined, ControlOutlined, CrownOutlined, SafetyCertificateOutlined, ThunderboltOutlined, UsergroupAddOutlined } from '@ant-design/icons';
import { Button, Col, Divider, Row, Space, Typography } from 'antd';
import useBreakpoint from 'antd/lib/grid/hooks/useBreakpoint';
import RegionStatusSection from '../components/RegionStatusSection';
import { getBreakpoint } from '../util';
import { ReactComponent as HonorLogo } from '../../public/honor.svg'
import colors from '../colors';
import DiscordButton from '../components/DiscordButton';
import { PropsWithChildren } from 'react';


const { Title, Text } = Typography;


const dividerStyle: React.CSSProperties = {
  textAlign: 'center',
  textTransform: 'uppercase',
  opacity: '70%',
  fontWeight: 600,
  filter: 'drop-shadow(0px 0px 8px #ffffff22)',
  margin: '20px 0px 20px 0px'
};

function WilderzoneButton() {
  return (
    <a target='_blank' href='https://wilderzone.live'>
      <Button
        className='discord-button'
        type='primary'
        size='large'
        style={{
          backgroundColor: colors.popoverBackground.hex,
          border: 'none',
          fontWeight: 500
        }}
      >
        {/* <Icon component={HonorLogo}/> */}
        WILDERZONE.LIVE
      </Button>
    </a>
  );
}

interface LandingSectionProps {
  title: string
}
function LandingSection(props: PropsWithChildren<LandingSectionProps>) {
  return (
    <>
      <Divider style={dividerStyle}>
        {props.title}
      </Divider>
      <div style={{
        maxWidth: '1000px',
        margin: '0 auto 25px auto',
        paddingLeft: '10px',
        paddingRight: '10px'
      }}>
        {props.children}
      </div>
  </>
  );

}

export default function LandingPage() {
  const breakpoint = useBreakpoint();

  const content = [
    {
      icon: ThunderboltOutlined,
      title: 'Performant',
      text: "Run full 28-player matches without lag or jankiness. Servers launch and update in < 1 minute. Move regions instantly to minimize latency.",
    },
    {
      icon: ControlOutlined,
      title: 'Customizable',
      text:
        <p>Easy-to-use interface backed by the full power of&nbsp;
          <a style={{color: 'white', textDecoration: 'underline'}} target='_blank' href='https://www.tamods.org/'>TAMods</a>. No coding/lua required. Brand New community maps already installed</p>,
    },
    {
      icon: CloudServerOutlined,
      title: 'Reliable',
      text: "Servers stay up as long as you want with 24/7 Cloud Hosting. Server history lets you expirement easily and rollback to a good config,",
    },
    {
      icon: SafetyCertificateOutlined,
      title: 'Secure',
      text: "Secure Against Cheaters and Abuse. Automatic admin access for your own servers. Easily share editing and admin rights with your community."
    }
  ];

  const titleStyle = {
    letterSpacing: '3.5px',
    marginTop: '0',
    marginBottom: '0',
    filter: 'drop-shadow(0px 0px 10px #1d84e355',
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
            color: '#1d84e3', //primary blue
            fontSize:breakpoint.md ? '128px' : '96px',
            filter: 'drop-shadow(0px 0px 10px #1d84e344'
          }}
          component={logo}/>
        <Title style={titleStyle}>
          &nbsp;LLAMAGRAB
        </Title>
        <Title level={3} style={titleStyle}>
          SERVERS
        </Title>
      </div>
      <LandingSection title='Tribes Community Server Hosting'>
        <Row justify='center' gutter={[16, 16]}>
          { content.map(item =>
            <Col key={item.title} style={{textAlign: 'center'}} xs={24} sm={12}>
                <item.icon
                      style={{
                      opacity: '70%',
                      padding: breakpoint.md ? '10px' : '5px 10px',
                      fontSize: '48px'}}
                    />
                <Title level={5} style={{opacity: '70%', textTransform: 'uppercase', letterSpacing: '1px'}}>
                  {item.title}
                </Title>
              <Text style={{opacity: '70%'}}>{item.text}</Text>
            </Col>
            )
          }
        </Row>
      </LandingSection>
      <LandingSection title='join us on'>
        <Row justify='center' gutter={[16, 16]} wrap>
          {/* <Col style={{textAlign:'center'}}>
            <span className='secondary-label'>get the scoop</span><br/>
            <WilderzoneButton/>
          </Col> */}
          <Col style={{textAlign:'center'}}>
            {/* <span className='secondary-label'>join us on</span><br/> */}
            <DiscordButton/>
          </Col>
        </Row>
      </LandingSection>

      <LandingSection title='Status'>
        <RegionStatusSection/>
      </LandingSection>
    </>
  );
};