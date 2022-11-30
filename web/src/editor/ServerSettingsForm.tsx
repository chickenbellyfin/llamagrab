import { Form, Select } from "antd";
import { useAuth } from "../auth";
import { ServerSettings, ServerStatus, User } from "../domain";

const { Option } = Select;

type ServerSettingsFormProps = {
  settings: ServerSettings
  regions: {[key: string]: string}
  status?: ServerStatus
  users: User[]
  onChange?: (settings: ServerSettings) => void
}

export default function ServerSettingsForm({ regions, settings, users, status, onChange }: ServerSettingsFormProps) {

  const auth = useAuth()
  const nonOwnerUsers = users.filter((user) => user.username != status?.owner)

  const onRegionChange = (value: string) => {
    if (onChange) {
      onChange(Object.assign({}, settings, {region: value}))
    }
  }

  const onEditorsChange = (value: number[]) => {
    if (onChange) {
      onChange(Object.assign({}, settings, {editors: value}))
    }
  }

  return (
    <Form
    labelCol={{span: 6}}
    wrapperCol={{span: 12}} onFinish={() => {}}>
    <Form.Item label="Region" name="region" rules={[{ required: true, message: 'Required' }]}>
    <Select
      style={{ width: 200 }}
      defaultValue={settings.region}
      onChange={onRegionChange}
      >
      {
        Object.keys(regions).map(key => {
          return <Option key={key} value={key}>{regions[key]}</Option>
        })
      }
    </Select>
    </Form.Item>

    <Form.Item
      label="Editors"
      extra="Other llamagrab users that can edit this server's settings">
      <Select
        disabled={!(status && auth.permissions.canShareServer(status))}
        showSearch
        onChange={onEditorsChange}
        defaultValue={settings.editors || []}
        mode="multiple"
        placeholder="Search for llamagrab users..."
        optionFilterProp="label"
        options={nonOwnerUsers.map(user => { return {label: user.username, value: user.id}})}>
      </Select>
    </Form.Item>
  </Form>
  );
}