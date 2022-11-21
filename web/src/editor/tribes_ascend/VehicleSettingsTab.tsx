import { Divider, Form, Space } from "antd";
import { InputInteger, InputPercent } from "../../editor/Inputs";
import { GameServerConfigTabProps } from "../../editor/tabHelpers";
import { VehicleProperties } from "./VehicleProperties";
import VehicleWeaponPropertiesSection from "./VehicleWeaponPropertiesSection";


export default function VehicleSettingsTab ({ config, updateCallbacks }: GameServerConfigTabProps) {

  const { update, updateInputNumber } = updateCallbacks;

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

      <Divider orientation='left'>Vehicle Properties</Divider>
      <Form.Item wrapperCol={{offset: 2}}>
        <Space direction='vertical' style={{width: '100%'}}>
        <VehicleProperties vehicleLabel='Grav Cycle' vehicleProperties={config.gravCycleProperties} onChange={update('gravCycleProperties')}/>
        <VehicleProperties vehicleLabel='Shrike' vehicleProperties={config.shrikeProperties} onChange={update('shrikeProperties')}/>
        <VehicleProperties vehicleLabel='Beowulf' vehicleProperties={config.beowulfProperties} onChange={update('beowulfProperties')}/>
        </Space>
      </Form.Item>

      <Divider orientation='left'>Vehicle Weapon Properties</Divider>
      <Form.Item wrapperCol={{offset: 2}}>
        <VehicleWeaponPropertiesSection properties={config.vehicleWeaponProperties} onChange={update('vehicleWeaponProperties')}/>
      </Form.Item>


    </Form>
  );
}
