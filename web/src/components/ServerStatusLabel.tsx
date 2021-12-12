import { Badge } from "antd";
import useBreakpoint from "antd/lib/grid/hooks/useBreakpoint";

const statusToBadge = {
  'running': 'success',
  'stopped':'error'
};

type ServerStatusProps = {
  status: string
}
export default function ServerStatusLabel(props: ServerStatusProps) {
  const breakpoint = useBreakpoint()
  let status = statusToBadge[props.status as keyof typeof statusToBadge]
  return <Badge status={status as any} text={breakpoint.md && props.status}/>
}