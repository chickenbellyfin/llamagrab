import { Form } from "antd";
import { InputInteger, InputPercent } from "./Inputs";
import { GameServerConfigTabProps } from "./tabHelpers";


export default function VehicleSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInputNumber } = updateCallbacks;

  return (
    <Form labelCol={{span: 6}} wrapperCol={{span: 14}}>
      <Form.Item label='Vehicle Health Multiplier' extra="Multiplier affecting all vehicles' health">
        <InputPercent        
          value={config.vehicleHealthMultiplier}
          onChange={updateInputNumber('vehicleHealthMultiplier')}
          min={0}
        />
      </Form.Item>
      
      <Form.Item label='Grav Cycle Limit'>
        <InputInteger
          min={0}
          value={config.gravCycleLimit}
          onChange={updateInputNumber('gravCycleLimit')}
          placeholder={'4'} />
      </Form.Item>

      <Form.Item label='Shrike Limit'>
        <InputInteger
          min={0}
          value={config.shrikeLimit}
          onChange={updateInputNumber('shrikeLimit')}
          placeholder={'2'} />
      </Form.Item>

      <Form.Item label='Beowulf Limit'>
        <InputInteger
          min={0}
          value={config.beowulfLimit}
          onChange={updateInputNumber('beowulfLimit')}
          placeholder={'2'} />
      </Form.Item>

      <Form.Item label='Grav Cycle Spawn Time'>
        <InputInteger
          min={0}
          value={config.gravCycleSpawnTime}
          onChange={updateInputNumber('gravCycleSpawnTime')}
          placeholder={'30'}
          addonAfter='secs' />
      </Form.Item>

      <Form.Item label='Shrike Spawn Time'>
        <InputInteger
          min={0}
          value={config.shrikeSpawnTime}
          onChange={updateInputNumber('shrikeSpawnTime')}
          placeholder={'120'}
          addonAfter='secs'  />
      </Form.Item>

      <Form.Item label='Beowulf Spawn Time'>
        <InputInteger
          min={0}
          value={config.beowulfSpawnTime}
          onChange={updateInputNumber('beowulfSpawnTime')}
          placeholder={'120'}
          addonAfter='secs'  />
      </Form.Item>
      
      
    </Form>
  );
}
