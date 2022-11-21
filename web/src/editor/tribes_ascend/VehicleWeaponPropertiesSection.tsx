import { DeleteOutlined, PlusCircleOutlined } from "@ant-design/icons";
import { Button, Card, List, Select, Space } from "antd";
import { useState } from "react";
import { VehicleWeaponPropertiesSpecSet } from "../../data";
import { ModProperty, VehicleWeaponProperties } from "../../domain";
import { Hint } from "../../editor/Inputs";
import ModPropertyList from "./ModPropertyList";


const weaponSelected = (w: VehicleWeaponProperties) => (w.vehicleWeapon)

type VehicleWeaponPropertiesWeaponProps = {
  vehicleWeaponProperties: VehicleWeaponProperties
  onChange: (value: VehicleWeaponProperties) => void
  onDelete: () => void
}

/**
 * A Single Vehicle weapon's properties
 */
function VehicleWeaponPropertiesWeapon({ vehicleWeaponProperties, onChange, onDelete }: VehicleWeaponPropertiesWeaponProps) {

  const setWeapon = (value: string) => {
    onChange(Object.assign(vehicleWeaponProperties, {vehicleWeapon: value}))
  }

  const setProperties = (value: ModProperty[]) => {
    onChange(Object.assign(vehicleWeaponProperties, {properties: value}))
  }

  return (
    <Card
      headStyle={{backgroundColor: 'rgba(0,0,0,.1)'}}
      className='form-card'
      title={
        <>
        <Space>
          <label>Vehicle Weapon:</label>
          <Select
            style={{width: '150px'}}
            placeholder='Weapon'
            onChange={setWeapon}
            value={vehicleWeaponProperties.vehicleWeapon}
            options={[
              {key: "Grav Cycle", label: "Grav Cycle", value: "Grav Cycle"},
              {key: "Shrike", label: "Shrike", value: "Shrike"},
              {key: "Beowulf Cannon", label: "Beowulf Cannon", value: "Beowulf Cannon"},
              {key: "Beowulf Chaingun", label: "Beowulf Chaingun", value: "Beowulf Chaingun"},
            ]}/>

        </Space>
        <Button onClick={onDelete} style={{float: 'right'}}><DeleteOutlined /></Button>
        </>
    }>

    { !weaponSelected(vehicleWeaponProperties) &&
      <Hint text='Select a vehicle weapon to modify'/>
    }

    <Space direction='vertical' style={{width:'100%'}}>
    { weaponSelected(vehicleWeaponProperties)  &&
      <ModPropertyList
        properties={vehicleWeaponProperties.properties}
        specSet={VehicleWeaponPropertiesSpecSet}
        onChange={setProperties}/>
    }

    </Space>
  </Card>);
}


type VehicleWeaponPropertiesListProps = {
  properties?: VehicleWeaponProperties[]
  onChange: (value: VehicleWeaponProperties[]) => void
}

export default function VehicleWeaponPropertiesListComponent(props: VehicleWeaponPropertiesListProps) {
  const [properties, setProperties] = useState(props.properties || [])

  const updateConfig = (updated: VehicleWeaponProperties[]) => {
    setProperties(updated)
    props.onChange(updated)
  }

  const addWeapon = () => {
    const updated = properties.concat([{}])
    updateConfig(updated)
  }

  const removeWeapon = (idx: number) => {
    properties.splice(idx, 1)
    updateConfig(properties)
  }

  const updateWeapon = (idx: number, value: VehicleWeaponProperties) => {
    properties[idx] = value;
    updateConfig(properties)
  }

  return (
    <div>
      <List split={false}>
        { properties.map((item, idx) => {
          return (
            <List.Item key={idx}>
              <VehicleWeaponPropertiesWeapon
                vehicleWeaponProperties={item}
                onChange={(value) => updateWeapon(idx, value)}
                onDelete={() => removeWeapon(idx)}/>
            </List.Item>);
        })}
      </List>
      <Button onClick={addWeapon}><PlusCircleOutlined /> Add Vehicle Weapon to Modify</Button>
    </div>
  );
}


