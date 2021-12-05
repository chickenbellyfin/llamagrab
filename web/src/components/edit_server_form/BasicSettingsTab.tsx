import { Form, Input, Select } from "antd";
import { GameServerConfigTabProps } from "./tabHelpers";
import Rules from "./validation";


export default function BasicSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { updateInput, update } = updateCallbacks;

  const adminListUpdate = update('admins')
  const handleAdminListChange = (values: Array<string>) => {
    // do not allow unverified accounts to be admins (also enforced server side)
    const verifiedNames = values.filter(v => !v.startsWith('unvrf'))
    adminListUpdate(verifiedNames)
  }

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
    <Form.Item 
      label='Server Admins'
      extra="These players can start, end, and switch maps using TAMods">
      <Select 
        placeholder="Enter community server usernames..."
        mode='tags' 
        value={config.admins || []}
        onChange={handleAdminListChange} 
        tokenSeparators={[',']}
        dropdownClassName='not-visible'/>
    </Form.Item>
    
  </Form>

  );
}
