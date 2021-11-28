import { Form, InputNumber, Radio, Switch } from "antd";
import { GameServerConfigTabProps } from "./tabHelpers";


export default function GameSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInput, updateRadio, updateSwitch, updateInputNumber } = updateCallbacks;

  return (
  <Form
  labelCol={{span: 4}}
  wrapperCol={{span: 14}}>
    <Form.Item 
      label='Team Assign Type:'>
      <Radio.Group
        defaultValue='balanced'
        buttonStyle='solid'
        value={config['teamAssignType']}
        onChange={updateRadio('teamAssignType')}>
        <Radio.Button value='balanced'>Balanced</Radio.Button>
        <Radio.Button value='unbalanced'>Unbalanced</Radio.Button>
        <Radio.Button value='auto'>Auto Assign</Radio.Button>
      </Radio.Group>
    </Form.Item>

    <Form.Item label='Auto Balance'>
      <Switch 
        defaultChecked
        checked={config['autoBalance']}
        onChange={updateSwitch('autoBalance')} />
    </Form.Item>

    <Form.Item label='Time Limit'>
      <InputNumber 
        precision={0}
        min={1}
        value={config['timeLimit']}
        onChange={updateInputNumber('timeLimit')}
        addonAfter='mins' />
    </Form.Item>          

    <Form.Item label='Overtime Limit'>
      <InputNumber
        precision={0}
        min={0}
        value={config['overtimeLimit']}
        onChange={updateInputNumber('overtimeLimit')}
        addonAfter='mins' />
    </Form.Item>

    <Form.Item label='Friendly Fire'>
      <Switch 
        defaultChecked 
        checked={config['friendlyFire']}
        onChange={updateSwitch('friendlyFire')} />
    </Form.Item>
    </Form>
  );
}
