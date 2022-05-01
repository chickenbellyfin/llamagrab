import { Form, Select } from "antd";
import { useState } from "react";
import { API, ServerSettings, ServerStatus, User } from "../../api";
import { useAuth } from "../../auth";
import Loader from "../Loader";

const { Option } = Select;

type ServerConfigFormProps = {
  settings: ServerSettings
  regions: {[key: string]: string}
  status?: ServerStatus
  users: User[]
  onChange?: (settings: ServerSettings) => void
}

function ServerConfigForm({ regions, settings, users, status, onChange }: ServerConfigFormProps) {
  
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


async function getServerSettings(serverId: number, settings?: ServerSettings): Promise<ServerConfigFormProps> {
  try {
    if (!settings) {
      settings = await API.Server.getServerSettings(serverId)
    }
    const status = await API.Server.getServerStatus(serverId)
    const regions = await API.Data.getRegions()
    const users = await API.Account.getAllUsers()
    return { settings, regions, users, status }
  } catch(error: any) {
    throw Error('Failed to get settings')
  }
}

type LoaderProps = {
  serverId: number
  settings?: ServerSettings
  onChange?: (settings: ServerSettings) => void
}
export default Loader<LoaderProps, ServerConfigFormProps>({
  loaderFunc: (props) => getServerSettings(props.serverId),
  componentBuilder: (result, props) => <ServerConfigForm {...result} {...props} />
});

type NewLoaderProps = {
  settings: ServerSettings,
  onChange?: (settings: ServerSettings) => void
}
export const NewServerConfigForm = Loader<NewLoaderProps, any>({
  loaderFunc: async (props) => {
    const regions = await API.Data.getRegions()
    const users = await API.Account.getAllUsers()
    return {regions, users}
  },
  componentBuilder: (result, props) => <ServerConfigForm {...result} {...props}/>
})