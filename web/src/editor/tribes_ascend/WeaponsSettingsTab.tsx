import { Divider, Form, Select } from "antd";
import { PlayerClass, weaponOptions } from "../../data";
import { GameServerConfigTabProps } from "../../editor/tabHelpers";
import { InputFloat } from "../Inputs";
import HardcodedLoadoutsForm from "./HardcodedLoadouts";
import { ItemPropertiesList } from "./ItemPropertiesSection";
import MutualExclusionList from "./MutualExclusions";


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
  const { update, updateInputNumber } = updateCallbacks;

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
      <Form.Item label='AoE Size Multiplier' extra='Multiplier affecting the size of all Area-of-Effect explosions'>
        <InputFloat
          min={0}
          value={config.aoeSizeMultiplier}
          onChange={updateInputNumber('aoeSizeMultiplier')}
          placeholder='1.0' />
      </Form.Item>
      <Form.Item label='AoE Damage Multiplier' extra='Multiplier affecting the damage done by Area-of-Effect explosions'>
        <InputFloat
          min={0}
          value={config.aoeDamageMultiplier}
          onChange={updateInputNumber('aoeDamageMultiplier')}
          placeholder='1.0' />
      </Form.Item>


      <Divider orientation='left'>Mutual Exclusions​</Divider>
      <MutualExclusionList mutualExclusions={config.mutualExclusions} onChange={update('mutualExclusions')}/>

      <Divider orientation='left'>Hardcoded Loadouts</Divider>
      <HardcodedLoadoutsForm
        config={config} updateCallbacks={updateCallbacks}/>
    </Form>
  );
}
