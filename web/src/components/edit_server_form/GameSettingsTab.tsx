import { Divider, Form, InputNumber, Switch } from "antd";
import {InputInteger} from "./Inputs";
import { GameServerConfigTabProps } from "./tabHelpers";


export default function GameSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInputNumber, updateSwitch } = updateCallbacks;

  return (
    <Form
    labelCol={{span: 6}}
    wrapperCol={{span: 12}}>


    <Divider orientation='left'>Time Settings</Divider>
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

    <Divider orientation='left'>Scoring</Divider>

    <Form.Item label='CTF Cap Limit'>
      <InputInteger
        min={1}
        value={config.ctfCapLimit}
        onChange={updateInputNumber('ctfCapLimit')}
        placeholder={'5'} 
        addonAfter='caps'/>
    </Form.Item>

    <Form.Item label='TDM Kill Limit'>
      <InputInteger
        min={1}
        value={config.tdmKillLimit}
        onChange={updateInputNumber('tdmKillLimit')}
        addonAfter='kills'
        placeholder={'100'} />
    </Form.Item>

    <Form.Item label='Arena Rounds'>
      <InputInteger
        min={1}
        value={config.arenaRounds}
        onChange={updateInputNumber('arenaRounds')}
        addonAfter='rounds'
        placeholder={'3'} />
    </Form.Item>

    <Form.Item label='Arena Lives' extra='Number of lives per round in Arena'>
      <InputInteger
        min={1}
        value={config.arenaLives}
        onChange={updateInputNumber('arenaLives')}
        addonAfter='lives'
        placeholder={'25'} />
    </Form.Item>

    <Form.Item label='Rabbit Score Limit'>
      <InputInteger
        min={1}
        value={config.rabbitScoreLimit}
        onChange={updateInputNumber('rabbitScoreLimit')}
        addonAfter='points'
        placeholder={'30'} />
    </Form.Item>

    <Form.Item label='CaH Score Limit' extra='Score to win in Capture and Hold'>
      <InputInteger
        min={1}
        value={config.cahScoreLimit}
        onChange={updateInputNumber('cahScoreLimit')}
        addonAfter='points'
        placeholder={'50'} />
    </Form.Item>

    <Form.Item label='CTF Blitz All Flag Move' extra="Whether both teams' flags move after a cap in Blitz">
      <Switch
        checked={config.ctfBlitzAllFlagsMove}
        onChange={updateSwitch('ctfBlitzAllFlagsMove')} />
    </Form.Item>


    </Form>
  );
}
