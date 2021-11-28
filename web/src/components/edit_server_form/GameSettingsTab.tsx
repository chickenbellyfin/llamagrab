import { Form, InputNumber, Radio, Switch } from "antd";
import {InputInteger} from "./Inputs";
import { GameServerConfigTabProps } from "./tabHelpers";


export default function GameSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInput, updateRadio, updateSwitch, updateInputNumber } = updateCallbacks;

  return (
  <Form
  labelCol={{span: 6}}
  wrapperCol={{span: 12}}>


    <Form.Item label='Time Limit'>
      <InputNumber 
        precision={0}
        min={1}
        value={config['timeLimit']}
        onChange={updateInputNumber('timeLimit')}
        addonAfter='mins'
        placeholder={'25'} />
    </Form.Item>          

    <Form.Item label='Overtime Limit'>
      <InputNumber
        precision={0}
        min={0}
        value={config['overtimeLimit']}
        onChange={updateInputNumber('overtimeLimit')}
        addonAfter='mins'
        placeholder={'10'} />
    </Form.Item>

    <Form.Item label='Warmup Time'>
      <InputNumber
        precision={0}
        min={0}
        value={config['warmupTime']}
        onChange={updateInputNumber('warmupTime')}
        addonAfter='secs'
        placeholder={'20'} />
    </Form.Item>

    <Form.Item label='Respawn Time'>
      <InputInteger
        min={0}
        value={config['respawnTime']}
        onChange={updateInputNumber('respawnTime')}
        addonAfter='secs'
        placeholder={'5'} />
    </Form.Item>

    <Form.Item label='Sniper Respawn Delay' extra='Additional respawn time incurred when the player has a sniper rifle'>
      <InputInteger
        min={0}
        value={config['sniperRespawnDelay']}
        onChange={updateInputNumber('sniperRespawnDelay')}
        addonAfter='secs'
        placeholder={'0'} />
    </Form.Item>

    <Form.Item label='Ammo Pickup Lifespan'>
      <InputInteger
        min={0}
        value={config['ammoPickupLifespan']}
        onChange={updateInputNumber('ammoPickupLifespan')}
        addonAfter='secs'
        placeholder={'15'} />
    </Form.Item>

    <Form.Item label='CTF Flag Timeout'>
      <InputInteger
        min={0}
        value={config['ctfFlagTimeout']}
        onChange={updateInputNumber('ctfFlagTimeout')}
        addonAfter='secs'
        placeholder={'40'} />
    </Form.Item>

    </Form>
  );
}
