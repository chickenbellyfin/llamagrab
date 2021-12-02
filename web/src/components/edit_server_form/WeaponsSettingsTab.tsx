import { Form, InputNumber, Radio, Select, Switch, Tabs, Typography } from "antd";
import { LabeledValue } from "antd/lib/select";
import { Weapon, WeaponsGrouped } from "../../data";
import { GameServerConfigTabProps } from "./tabHelpers";


const { TabPane } = Tabs;
const { Option, OptGroup } = Select;

type PlayerClass = 'Light' | 'Medium' | 'Heavy'

type ClassSettingsProps = {
  selected?: Array<string>
  clazz: PlayerClass
  onChange: (selected: Array<string>) => void
}

function ClassSettings ({selected, clazz, onChange}: ClassSettingsProps) {
   
  const classWeapons = WeaponsGrouped[clazz];

  const handleOnChange = (values: Array<LabeledValue>) => {
   onChange(values.map(v => v.key as string))
  }

  return (
    <Form.Item label={`${clazz} Weapon Bans`}>
      <Select 
          size='large'
          mode='multiple'
          allowClear
          value={selected}
          onChange={onChange}
          >
          { 
            Object.keys(classWeapons).map(group => {
              return (
                <OptGroup label={group.toUpperCase()}>
                  { classWeapons[group].map(weapon => {
                    return <Option key={weapon.key} value={weapon.key}>{weapon.name}</Option>
                  })}
                </OptGroup>
              );
            })
          }
        </Select>
      </Form.Item>
  );
}

export default function WeaponsSettingsTab (
  { config, updateCallbacks }: GameServerConfigTabProps
) {


  const { updateInput, updateRadio, updateSwitch, updateInputNumber, update } = updateCallbacks;

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
    </Form>
  );
}
