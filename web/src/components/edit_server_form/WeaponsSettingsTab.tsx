import {  Divider, Form,  Select, Switch, Table } from "antd";

import { PlayerClass, weaponOptions } from "../../data";
import HardcodedLoadoutsForm from "./HardcodedLoadouts";
import { ItemPropertiesList } from "./ItemPropertiesSection";
import { GameServerConfigTabProps } from "./tabHelpers";


type ClassSettingsProps = {
  selected?: Array<string>
  clazz: PlayerClass
  onChange: (selected: Array<string>) => void
}

function ClassSettings ({selected, clazz, onChange}: ClassSettingsProps) { 

  return (
    <Form.Item label={`${clazz} Weapon Bans`}>
      <Select 
          size='large'
          mode='multiple'
          allowClear
          value={selected || []}
          onChange={onChange}
          >
          { weaponOptions(clazz) }
        </Select>
      </Form.Item>
  );
}

export default function WeaponsSettingsTab ({ config, updateCallbacks }: GameServerConfigTabProps) {
  const { update } = updateCallbacks;

  return (
    <Form labelCol={{span: 6}} wrapperCol={{span: 16}}>
      <ClassSettings
        selected={config.lightWeaponBans}
        clazz={'Light' as PlayerClass}
        onChange={update('lightWeaponBans')}/>
      <ClassSettings
        selected={config.mediumWeaponBans}
        clazz={'Medium' as PlayerClass}
        onChange={update('mediumWeaponBans')}/>
      <ClassSettings
        selected={config.heavyWeaponBans}
        clazz={'Heavy' as PlayerClass}
        onChange={update('heavyWeaponBans')}/>
      
      <Divider orientation='left'>Item Properties</Divider>
      <Form.Item wrapperCol={{offset: 2}}>
        <ItemPropertiesList configItemProperties={config.itemProperties} onChange={update('itemProperties')}/>
      </Form.Item>

      <Divider orientation='left'>Hardcoded Loadouts</Divider>
      <HardcodedLoadoutsForm
        config={config} updateCallbacks={updateCallbacks}/>
    </Form>
  );
}
