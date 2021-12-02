import { Form, Input } from "antd";
import { GameServerConfigTabProps } from "./tabHelpers";
import Rules from "./validation";


export default function BasicSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInput, updateRadio, updateSwitch, updateInputNumber } = updateCallbacks;

  return (
    <Form
    labelCol={{span: 6}}
    wrapperCol={{span: 12}}
    >

    <Form.Item 
      label='Name'
      name='name'
      rules={[Rules.required, Rules.allowedCharacters]}>
      <Input
        defaultValue={config['displayName']} value={config['displayName']}
        onChange={updateInput('displayName')}/>
    </Form.Item>

    <Form.Item name='description' label='Description' rules={[Rules.allowedCharacters]}>
      <Input 
        defaultValue={config['description']}
        onChange={updateInput('description')}/>
    </Form.Item>

    <Form.Item name='password' label='Server Password' rules={[Rules.allowedCharacters]}>
      <Input.Password
        defaultValue={config['password']}
        onChange={updateInput('password')}/>
    </Form.Item>
    
    <Form.Item name='adminPassword' label='Admin Password' rules={[Rules.allowedCharacters]}>
      <Input.Password
        defaultValue={config['adminPassword']}
        onChange={updateInput('adminPassword')}/>
    </Form.Item>
  </Form>

  );
}
