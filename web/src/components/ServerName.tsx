import { LockOutlined } from "@ant-design/icons";
import { Tooltip } from "antd";
import { ServerStatus } from "../domain";

interface ServerNameProps {
    status: ServerStatus
}
export default function ServerName({status}: ServerNameProps) {
  return (
    <>
      {status.isPrivate && <Tooltip title='Private Server'><LockOutlined/></Tooltip>}&nbsp;
      {status.name}
    </>
  )
}