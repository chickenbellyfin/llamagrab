import { Form, InputNumber, Radio, Switch, Typography } from "antd";
import {InputInteger, InputPercent } from "./Inputs";
import { GameServerConfigTabProps } from "./tabHelpers";


export default function TeamSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInput, updateRadio, updateSwitch, updateInputNumber } = updateCallbacks;

  return (
    <Form labelCol={{span: 6}} wrapperCol={{span: 12}}>
      <Form.Item label='Max Players' extra='Maximum players in the server'>
        <InputInteger
          min={0}
          value={config['maxPlayers']}
          onChange={updateInputNumber('maxPlayers')}
          placeholder={'32'} />
      </Form.Item>
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
    
    <Form.Item label='Friendly Fire'>
      <Switch 
        defaultChecked 
        checked={config['friendlyFire']}
        onChange={updateSwitch('friendlyFire')} />
    </Form.Item>

    <Form.Item label='Friendly Fire Multiplier'>
      <InputPercent        
        value={config.friendlyFireMultiplier}
        onChange={updateInputNumber('friendlyFireMultiplier')}
        min={0}
      />
    </Form.Item>

    <Form.Item label='Naked Spawn' extra='Whether players should spawn naked (as lights without their loadout)'>
      <Switch 
        checked={config['nakedSpawn']}
        onChange={updateSwitch('nakedSpawn')} />
    </Form.Item>
    </Form>
  );
}