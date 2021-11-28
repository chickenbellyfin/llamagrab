import { Form, InputNumber, Radio, Switch, Typography } from "antd";
import { GameServerConfigTabProps } from "./tabHelpers";


export default function VehicleSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInput, updateRadio, updateSwitch, updateInputNumber } = updateCallbacks;

  return (
    <Form labelCol={{span: 4}} wrapperCol={{span: 14}}>
      <Typography.Title level={2} type="secondary">Coming Soon</Typography.Title>
    </Form>
  );
}
