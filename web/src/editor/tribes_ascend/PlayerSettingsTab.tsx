import { Checkbox, Divider, Form, Space, Switch } from "antd";
import { PlayerClass } from "../../data";
import { InputFloat, InputInteger } from "../../editor/Inputs";
import { GameServerConfigTabProps } from "../../editor/tabHelpers";
import { ClassProperties } from "./ClassProperties";

interface DisabledEquipPointsProps {
  clazz: PlayerClass
  value?: string[]
  onChange: (value: string[]) => void
}
function DisabledEquipPoints(props: DisabledEquipPointsProps) {
  return (
    <Form.Item label={props.clazz} wrapperCol={{span:18}}>
      <Checkbox.Group
        options={['Melee', 'Primary', 'Secondary', 'Tertiary', 'Pack', 'Belt', 'LaserTarget']}
        value={props.value || []}
        onChange={e => props.onChange(e as string[])}/>
    </Form.Item>
  );
}

export default function PlayerSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInputNumber, update, updateSwitch } = updateCallbacks;

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
      

      <Form.Item label='Skiing Enabled'>
        <Switch
          checked={config.skiingEnabled ?? true}
          onChange={updateSwitch('skiingEnabled')} />
      </Form.Item>

      <Form.Item 
        label='Use GOTY Shield Pack' 
        extra="Taking damage with shields will not block regen, and heavy shield pack will not reduce impulse received when active">
        <Switch
          checked={config.useGotyShieldPack}
          onChange={updateSwitch('useGotyShieldPack')} />
      </Form.Item>

      <Form.Item label='Inventory Station Restore Energy'>
        <Switch
          checked={config.inventoryStationRestoreEnergy}
          onChange={updateSwitch('inventoryStationRestoreEnergy')} />
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

      <Divider orientation='left'>Disabled Equip Points</Divider>
      <DisabledEquipPoints clazz='Light' value={config.lightDisabledEquipPoints} onChange={update('lightDisabledEquipPoints')}/>
      <DisabledEquipPoints clazz='Medium' value={config.mediumDisabledEquipPoints} onChange={update('mediumDisabledEquipPoints')}/>
      <DisabledEquipPoints clazz='Heavy' value={config.heavyDisabledEquipPoints} onChange={update('heavyDisabledEquipPoints')}/>


      <Divider orientation='left'>Class Properties</Divider>
      <Form.Item wrapperCol={{/*empty wrapper col makes it 100% width*/}}>
        <Space direction='vertical' style={{width: '100%'}}>
        <ClassProperties classLabel='Light' classProperties={config.lightClassProperties} onChange={update('lightClassProperties')}/>
        <ClassProperties classLabel='Medium' classProperties={config.mediumClassProperties} onChange={update('mediumClassProperties')}/>
        <ClassProperties classLabel='Heavy' classProperties={config.heavyClassProperties} onChange={update('heavyClassProperties')}/>
        </Space>
      </Form.Item>
    </Form>

  );
}
