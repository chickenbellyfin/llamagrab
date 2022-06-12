import { Form, Select } from "antd";
import { useState } from "react";
import { ServerSettings, ServerStatus, User } from "../api";
import { useAuth } from "../auth";

const { Option } = Select;

type ServerSettingsFormProps = {
  settings: ServerSettings
  regions: {[key: string]: string}
  status?: ServerStatus
  users: User[]
  onChange?: (settings: ServerSettings) => void
}

export default function ServerSettingsForm({ regions, settings, users, status, onChange }: ServerSettingsFormProps) {

  const [updatedSettings, setSettings] = useState(settings)
  const auth = useAuth()

  const onRegionChange = (value: string) => {
    const newState = Object.assign(updatedSettings, {region: value})
    setSettings(newState)
    if (onChange) {
      onChange(updatedSettings)
    }
  }

  const onEditorsChange = (value: number[]) => {
    const newState = Object.assign(updatedSettings, {editors: value})
    setSettings(newState)
    if (onChange) {
      onChange(updatedSettings)
    }
  }

  const isOwner = status != null ? (status?.owner === auth.user?.username) : true;

  return (
    <Form
    labelCol={{span: 6}}
    wrapperCol={{span: 12}} onFinish={() => {}}>
    <Form.Item label="Region" name="region" rules={[{ required: true, message: 'Required' }]}>
    <Select
      style={{ width: 200 }}
      defaultValue={updatedSettings.region}
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
        disabled={!isOwner}
        showSearch
        onChange={onEditorsChange}
        defaultValue={updatedSettings.editors || []}
        mode="multiple"
        placeholder="Search for llamagrab users..."
        optionFilterProp="label"
        options={users.map(user => { return {label: user.username, value: user.id}})}>
      </Select>
    </Form.Item>

  </Form>
  );
}