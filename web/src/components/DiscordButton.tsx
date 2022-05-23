import Icon from "@ant-design/icons";
import { Button } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";
import { ReactComponent as DiscordLogo } from '../../public/discord.svg'

interface DiscordButtonProps {
    size?: 'small' | 'middle' | 'large'
    responsive?: boolean
}
export default function DiscordButton(props: DiscordButtonProps) {
  const breakpoint = useBreakpoint();
  return (
    <a target='_blank' href='https://discord.gg/dd8JgzJ'>
      <Button
        type='primary'
        size={props.size !== undefined ? props.size : 'large'}
        style={{ backgroundColor: '#5865F2', border: 'none', fontWeight: 500 }}
      >
        <Icon component={DiscordLogo} />{(!props.responsive || breakpoint.sm) ? 'DISCORD' : null}
      </Button>
    </a>
  );
}