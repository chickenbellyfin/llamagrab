import { Divider, Form, Radio, Switch } from "antd";
import { InputInteger, InputPercent } from "../../editor/Inputs";
import { GameServerConfigTabProps } from "../../editor/tabHelpers";


export default function TeamSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateRadio, updateSwitch, updateInputNumber } = updateCallbacks;

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
        checked={config['autoBalance']}
        onChange={updateSwitch('autoBalance')} />
    </Form.Item>

    <Form.Item label='Friendly Fire'>
      <Switch
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

    <Form.Item label='Friendly Damage Kick Limit'>
      <InputInteger
        placeholder='0 (no limit)'
        value={config.friendlyFireDamageKickLimit}
        onChange={updateInputNumber('friendlyFireDamageKickLimit')}
        min={0}
      />
    </Form.Item>

    <Form.Item label='Friendly Kill Kick Limit'>
      <InputInteger
        placeholder='0 (no limit)'
        value={config.friendlyFireKillKickLimit}
        onChange={updateInputNumber('friendlyFireKillKickLimit')}
        min={0}
      />
    </Form.Item>

    <Form.Item label='Base Destruction Kick Limit'>
      <InputInteger
        placeholder='0 (no limit)'
        value={config.baseDestructionKickLimit}
        onChange={updateInputNumber('baseDestructionKickLimit')}
        min={0}
      />
    </Form.Item>

    <Form.Item label='Light Limit' extra='Maximum light players per team'>
      <InputInteger
        min={0}
        value={config.lightCountLimit}
        onChange={updateInputNumber('lightCountLimit')}
        placeholder={'32'} />
    </Form.Item>
    <Form.Item label='Medium Limit' extra='Maximum medium players per team'>
      <InputInteger
        min={0}
        value={config.mediumCountLimit}
        onChange={updateInputNumber('mediumCountLimit')}
        placeholder={'32'} />
    </Form.Item>
    <Form.Item label='Heavy Limit' extra='Maximum heavy players per team'>
      <InputInteger
        min={0}
        value={config.heavyCountLimit}
        onChange={updateInputNumber('heavyCountLimit')}
        placeholder={'32'} />
    </Form.Item>

    <Form.Item label='Naked Spawn' extra='Whether players should spawn naked (as lights without their loadout)'>
      <Switch
        checked={config['nakedSpawn']}
        onChange={updateSwitch('nakedSpawn')} />
    </Form.Item>

    <Divider orientation='left'>Base Settings</Divider>

    <Form.Item label='Base Assets' extra="Whether turrets and sensors are enabled">
      <Switch
        checked={config.baseAssets ?? true}
        onChange={updateSwitch('baseAssets')} />
    </Form.Item>
    <Form.Item label='Powered Deployables' extra="Whether deployables (e.g. turrets) require generator power">
      <Switch
        checked={config.poweredDeployables ?? true}
        onChange={updateSwitch('poweredDeployables')} />
    </Form.Item>
    <Form.Item label='Generator Regen' extra="Whether the generator regenerates automatically over time">
      <Switch
        checked={config.generatorRegen}
        onChange={updateSwitch('generatorRegen')} />
    </Form.Item>
    <Form.Item label='Generator Destroyable'>
      <Switch
        checked={config.generatorDestroyable ?? true}
        onChange={updateSwitch('generatorDestroyable')} />
    </Form.Item>
    
    <Form.Item label='Base Asset Friendly Fire'>
      <Switch
        checked={config.baseAssetFriendlyFire}
        onChange={updateSwitch('baseAssetFriendlyFire')} />
    </Form.Item>

    <Form.Item label='Deployable Asset Friendly Fire'>
      <Switch
        checked={config.deployableFriendlyFire}
        onChange={updateSwitch('deployableFriendlyFire')} />
    </Form.Item>

    </Form>
  );
}