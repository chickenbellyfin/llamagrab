import { DeleteOutlined, PlusCircleOutlined } from "@ant-design/icons";
import { Button, Card, List, Select, Space} from "antd";
import { useState } from "react";
import {  ItemProperties, ModProperty } from "../../api";
import { ItemPropertiesSpecSet, ModPropertySpecSet, PlayerClass, ValueModsSpecSet, weaponOptions } from "../../data";
import { Hint } from "../../editor/Inputs";
import ModPropertyList from "./ModPropertyList";


const weaponSelected = (w: ItemProperties) => (w.playerClass && w.weapon)

type ItemPropertiesWeaponProps = {
  itemProperties: ItemProperties
  specSet: ModPropertySpecSet
  onChange: (value: ItemProperties) => void
  onDelete: () => void
}
function ItemPropertiesWeapon({ itemProperties, specSet, onChange, onDelete }: ItemPropertiesWeaponProps) {
  const setClazz = (clazz: PlayerClass) => {
    onChange(Object.assign(itemProperties, {playerClass: clazz, weapon: undefined}))
  }

  const setWeapon = (value: string) => {
    onChange(Object.assign(itemProperties, {weapon: value}))
  }

  const setProperties = (value: ModProperty[]) => {
    onChange(Object.assign(itemProperties, {properties: value}))
  }

  return (
    <Card
      headStyle={{backgroundColor: 'rgba(0,0,0,.1)'}}
      className='form-card'
      title={
        <>
        <Space>
          <label>Weapon:</label>
          <Select
            style={{width: '100px'}}
            placeholder='Class'
            onChange={setClazz}
            value={itemProperties.playerClass as PlayerClass}
            options={[
              {key: "Light", label: "Light", value: "Light"},
              {key: "Medium", label: "Medium", value: "Medium"},
              {key: "Heavy", label: "Heavy", value: "Heavy"},
            ]}/>

          <Select
            style={{width: '200px'}}
            placeholder='Weapon'
            onChange={setWeapon}
            value={itemProperties.weapon}
            disabled={itemProperties.playerClass === undefined}>
            {itemProperties.playerClass && weaponOptions(itemProperties.playerClass as PlayerClass)}
          </Select>

        </Space>
        <Button onClick={onDelete} style={{float: 'right'}}><DeleteOutlined /></Button>
        </>
    }>

    { !weaponSelected(itemProperties) &&
      <Hint text='Select a weapon to modify'/>
    }

    <Space direction='vertical' style={{width:'100%'}}>
    { weaponSelected(itemProperties)  &&
      <ModPropertyList
        properties={itemProperties.properties}
        specSet={specSet}
        onChange={setProperties}/>
    }

    </Space>
  </Card>);
}

type ItemPropertiesListBuilderProps = {
  specSet: ModPropertySpecSet
}
type ItemPropertiesListProps = {
  configItemProperties?: ItemProperties[]
  onChange: (value: ItemProperties[]) => void
}

function ItemPropertiesListBuilder ({specSet}: ItemPropertiesListBuilderProps) {
  return function ItemPropertiesListComponent(props: ItemPropertiesListProps) {

    const [itemProperties, setItemProperties] = useState(props.configItemProperties || [])

    const updateConfig = (updated: ItemProperties[]) => {
      setItemProperties(updated)
      props.onChange(updated)
    }

    const addWeapon = () => {
      const updated = itemProperties.concat([{}])
      updateConfig(updated)
    }

    const removeWeapon = (idx: number) => {
      itemProperties.splice(idx, 1)
      updateConfig(itemProperties)
    }

    const updateWeapon = (idx: number, value: ItemProperties) => {
      itemProperties[idx] = value;
      updateConfig(itemProperties)
    }

    return (
      <div>
        <List split={false}>
          { itemProperties.map((item, idx) => {
            return (
              <List.Item key={idx}>
                <ItemPropertiesWeapon
                  itemProperties={item}
                  specSet={specSet}
                  onChange={(value) => updateWeapon(idx, value)}
                  onDelete={() => removeWeapon(idx)}/>
              </List.Item>);
          })}
        </List>
        <Button onClick={addWeapon}><PlusCircleOutlined /> Add Weapon to Modify</Button>
      </div>
    );
  }
}

export const ItemPropertiesList = ItemPropertiesListBuilder({
  specSet: ItemPropertiesSpecSet
});

export const ItemValueModsList = ItemPropertiesListBuilder({
  specSet: ValueModsSpecSet
})