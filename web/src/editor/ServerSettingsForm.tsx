import { Form, Select } from "antd";
import { useState } from "react";
import { API, ServerSettings, ServerStatus, User } from "../api";
import { useAuth } from "../auth";
import Loader from "../components/Loader";

const { Option } = Select;

type ServerSettingsFormProps = {
  settings: ServerSettings
  regions: {[key: string]: string}
  status?: ServerStatus
  users: User[]
  onChange?: (settings: ServerSettings) => void
}

function ServerSettingsForm({ regions, settings, users, status, onChange }: ServerSettingsFormProps) {

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


async function getServerSettings(serverId: number, settings?: ServerSettings): Promise<ServerSettingsFormProps> {
  let settingsPromise;
  try {
    if (!settings) {
      settingsPromise = API.Server.getServerSettings(serverId)
    } else {
      settingsPromise = Promise.resolve(settings);
    }
    const status = API.Server.getServerStatus(serverId)
    const regions = API.Data.getRegions()
    const users = API.Account.getAllUsers()
    return {
      settings: await settingsPromise,
      regions: await regions,
      users: await users,
      status: await status
    }
  } catch(error: any) {
    throw Error('Failed to get settings')
  }
}

type LoaderProps = {
  serverId: number
  settings?: ServerSettings
  onChange?: (settings: ServerSettings) => void
}
export default Loader<LoaderProps, ServerSettingsFormProps>({
  loaderFunc: (props) => getServerSettings(props.serverId),
  componentBuilder: (result, props) => <ServerSettingsForm {...result} {...props} />
});

type NewLoaderProps = {
  settings: ServerSettings,
  onChange?: (settings: ServerSettings) => void
}
export const NewServerSettingsForm = Loader<NewLoaderProps, any>({
  loaderFunc: async (props) => {
    const regions = API.Data.getRegions()
    const users = API.Account.getAllUsers()
    return {
      regions: await regions,
      users: await users
    }
  },
  componentBuilder: (result, props) => <ServerSettingsForm {...result} {...props}/>
})