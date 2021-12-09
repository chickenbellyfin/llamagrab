import { Badge } from "antd";

const statusToBadge = {
  'running': 'success',
  'stopped':'error'
};

type ServerStatusProps = {
  status: string
}
export default function ServerStatusLabel(props: ServerStatusProps) {
  let status = statusToBadge[props.status as keyof typeof statusToBadge]
  return <Badge status={status as any} text={props.status}/>
}