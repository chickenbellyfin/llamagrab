import { Divider, Form, Input, Select } from "antd";
import { InputFloat, InputInteger } from "./Inputs";
import { GameServerConfigTabProps } from "./tabHelpers";
import Rules from "./validation";


export default function PlayerSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInputNumber } = updateCallbacks;

  

  return (
    <Form
    labelCol={{span: 6}}
    wrapperCol={{span: 12}}>
      <Form.Item label='Energy Multiplier' extra='Multiplier affecting the energy pools of all players'>
        <InputFloat
          min={0}
          value={config.energyMultiplier}
          onChange={updateInputNumber('energyMultiplier')}
          placeholder='1.0' />
      </Form.Item>
      <Divider orientation='left'>Flag Drag</Divider>
      <Form.Item label='Light Flag Drag' extra='Speed at which flag-drag occurs for lights'>
        <InputInteger
          min={0}
          value={config.flagDragLight}
          onChange={updateInputNumber('flagDragLight')}
          addonAfter='UU/S' />
      </Form.Item>
      <Form.Item label='Medium Flag Drag' extra='Speed at which flag-drag occurs for mediums'>
        <InputInteger
          min={0}
          value={config.flagDragMedium}
          onChange={updateInputNumber('flagDragMedium')}
          addonAfter='UU/S' />
      </Form.Item>
      <Form.Item label='Heavy Flag Drag' extra='Speed at which flag-drag occurs for heavies'>
        <InputInteger
          min={0}
          value={config.flagDragHeavy}
          onChange={updateInputNumber('flagDragHeavy')}
          addonAfter='UU/S' />
      </Form.Item>
      <Form.Item label='Flag Drag Deceleration'>
        <InputInteger
          min={0}
          value={config.flagDragDeceleration}
          onChange={updateInputNumber('flagDragDeceleration')}
          addonAfter='UU/S²'
          placeholder='0' />
      </Form.Item>
    </Form>

  );
}
