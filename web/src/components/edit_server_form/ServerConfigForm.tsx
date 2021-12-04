import { Form, Select } from "antd";
import { useEffect, useState } from "react";
import { API, ServerSettings } from "../../api";
import Loader from "../Loader";

const { Option } = Select;

type ServerConfigFormProps = {
  settings: ServerSettings
  regions: {[key: string]: string}
  onChange?: (settings: ServerSettings) => void
}

function ServerConfigForm({ regions, settings, onChange }: ServerConfigFormProps) {
  
  const [updatedSettings, setSettings] = useState(settings)

  const onRegionChange = (value: string) => {
    const newState = Object.assign(updatedSettings, {region: value})
    setSettings(newState)
    if (onChange) {
      onChange(updatedSettings)
    }
  }

  console.log(updatedSettings)
  return (
    <Form layout='inline' onFinish={() => {}}>
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

  </Form>
  );
}


async function getServerSettings(serverId: number, settings?: ServerSettings): Promise<ServerConfigFormProps> {
  try {
    if (!settings) {
      settings = await API.Server.getServerSettings(serverId)
    }
    const regions = await API.Data.getRegions()
    return { settings, regions }
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
  loaderFunc: (props) => API.Data.getRegions(),
  componentBuilder: (regions, props) => <ServerConfigForm regions={regions} {...props}/>
})