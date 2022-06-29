import Icon from "@ant-design/icons";
import { Button } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { ReactComponent as DiscordLogo } from '../../public/discord.svg';
import './DiscordButton.less';

interface DiscordButtonProps {
    size?: 'small' | 'middle' | 'large'
    responsive?: boolean
}
export default function DiscordButton(props: DiscordButtonProps) {
  const breakpoint = useBreakpoint();
  return (
    <a target='_blank' href='https://discord.gg/dd8JgzJ'>
      <Button
        className='discord-btn'
        type='primary'
        size={props.size !== undefined ? props.size : 'large'}>
        <Icon component={DiscordLogo} />{(!props.responsive || breakpoint.sm) ? 'DISCORD' : null}
      </Button>
    </a>
  );
}