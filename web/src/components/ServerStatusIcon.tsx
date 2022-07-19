import { CheckCircleFilled, CheckCircleOutlined, ClockCircleFilled, ClockCircleOutlined, CloseCircleFilled, CloseCircleOutlined, PauseCircleFilled, PauseCircleOutlined, QuestionCircleFilled, QuestionCircleOutlined, SyncOutlined } from "@ant-design/icons";
import { Tooltip } from "antd";
import colors from '../colors';
import { Status } from "../domain";
import './ServerStatusIcon.css';

const ICONS = {
  'running': {
    outlined: CheckCircleOutlined,
    filled: CheckCircleFilled,
    color: colors.success.hex,
    label: 'Running'
  },
  'starting': {
    outlined: ClockCircleOutlined,
    filled: ClockCircleFilled,
    color: colors.warning.hex,
    label: 'Starting',
    className: 'pulse'
  },
  'restarting': {
    outlined: SyncOutlined,
    filled: SyncOutlined,
    color: colors.warning.hex,
    label: 'Restarting',
    spin: true
  },
  'stopping': {
    outlined: ClockCircleOutlined,
    filled: ClockCircleFilled,
    color: colors.warning.hex,
    label: 'Stopping',
    className: 'pulse'
  },
  'offline': {
    outlined: CloseCircleOutlined,
    filled: CloseCircleFilled,
    color: colors.error.hex,
    label: 'Offline'
  },
  'unknown': {
    outlined: QuestionCircleOutlined,
    filled: QuestionCircleFilled,
    color: colors.disabled.hex,
    label: 'Unknown'
  },
  'disabled': {
    outlined: PauseCircleOutlined,
    filled: PauseCircleFilled,
    color: colors.disabled.hex,
    label: 'Disabled'
  },
}

interface ServerStatusIconProps {
  status: Status | boolean,
  filled?: boolean
  showLabel?: boolean
}
export default function ServerStatusIcon(props: ServerStatusIconProps) {
  let presetKey: Status;
  if (typeof props.status === 'boolean') {
    presetKey = props.status ? 'running': 'offline'
  } else {
    presetKey = props.status
  }

  const preset = ICONS[presetKey]
  const IconClass = props.filled ? preset.filled : preset.outlined;
  const icon = <IconClass
    className={(preset as any)['className']}
    style={{ color: preset.color }}
    spin={(preset as any)['spin']}/>
  return (props.showLabel ?
    <span style={{alignItems: 'middle'}}>
      <span style={{marginRight: '5px'}}>{icon}</span>{preset.label}
    </span>
    :
    <Tooltip title={preset.label}>
      {icon}
    </Tooltip>
  )
}
