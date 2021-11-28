import { Form, Switch } from "antd";
import MapSelector from "./MapSelector";
import { GameServerConfigTabProps } from "./tabHelpers";


export default function MapRotationSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { update } = updateCallbacks;

  return (
    <Form labelCol={{span: 4}} wrapperCol={{span: 14}}>
    <Form.Item label='Map Voting'>
      <Switch defaultChecked onChange={(checked: boolean) => null} />
    </Form.Item>

    <br/>
    <MapSelector 
      gameType='CTF'
      mapList={config['maps']}
      onChange={update('maps')}/>
  </Form>
  );
}
