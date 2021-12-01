import { Checkbox, Form, Switch } from "antd";
import { useState } from "react";
import { MapsByKey } from "../../data";
import MapSelector from "./MapSelector";
import { GameServerConfigTabProps } from "./tabHelpers";

export default function MapRotationSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const inferredGameModes = Array.from(new Set(config.maps.map(m => {
    console.log(`keying ${m}`);
    return MapsByKey[m].gameMode})));
  const [gameModes, setGameModes] = useState(inferredGameModes);
  

  const { updateSwitch, update } = updateCallbacks;



  return (
    <Form labelCol={{span: 4}} wrapperCol={{span: 14}}>
    
    <Form.Item label='Map Voting'>
      <Switch checked={config.mapVoting} onChange={updateSwitch('mapVoting')} />
    </Form.Item>
    <br/>

    <Form.Item label="Game Types" extra="You can have multiple game modes on a server. ">
    <Checkbox.Group
      options={['CTF', 'Arena', 'TDM', 'Rabbit', 'Blitz', 'CaH']}
      value={gameModes}
      onChange={(e) => setGameModes(e as string[])}
    />
    </Form.Item>
    <MapSelector 
      gameTypes={gameModes}
      mapList={config['maps']}
      onChange={update('maps')}/>
  </Form>
  );
}
