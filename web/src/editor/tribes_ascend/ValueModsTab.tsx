import { Divider, Form, Space } from "antd";
import { GameServerConfigTabProps } from "../../editor/tabHelpers";
import { ClassValueMods } from "./ClassProperties";
import { ItemValueModsList } from "./ItemPropertiesSection";


export default function ValueModsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {

  const { update } = updateCallbacks;


  return (
    <Form
    labelCol={{span: 6}}
    wrapperCol={{span: 12}}
    >

      <Divider orientation='left'>Class Value Mods</Divider>
      <Form.Item wrapperCol={{offset: 2}}>
        <Space direction='vertical' style={{width: '100%'}}>
        <ClassValueMods classLabel='Light' classProperties={config.lightValueMods} onChange={update('lightValueMods')}/>
        <ClassValueMods classLabel='Medium' classProperties={config.mediumValueMods} onChange={update('mediumValueMods')}/>
        <ClassValueMods classLabel='Heavy' classProperties={config.heavyValueMods} onChange={update('heavyValueMods')}/>
      </Space>
    </Form.Item>


    <Divider orientation='left'>Weapon Value Mods</Divider>
    <Form.Item wrapperCol={{offset: 2}}>
        <ItemValueModsList configItemProperties={config.itemValueMods} onChange={update('itemValueMods')}/>
    </Form.Item>
  </Form>

  );
}
