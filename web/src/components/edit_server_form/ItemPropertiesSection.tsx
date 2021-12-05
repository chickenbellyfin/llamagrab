import { CheckCircleOutlined, DeleteOutlined, ExclamationCircleOutlined, PlusCircleOutlined } from "@ant-design/icons";
import { Button, Card, Col, List, Popover, Row, Select, Space, Switch} from "antd";
import { useState } from "react";
import { GameServerConfig, ItemProperties, ItemProperty } from "../../api";
import { ItemPropertiesByName, ItemPropertyOptions, PlayerClass, weaponOptions } from "../../data";
import { Hint, InputFloat, InputInteger } from "./Inputs";
import { UpdateCallbacks } from "./tabHelpers";


const weaponSelected = (w: ItemProperties) => (w.playerClass && w.weapon)

const { Option, OptGroup } = Select;

const itemPropertyOptions = Object.keys(ItemPropertyOptions).map((group) => {
  return (
    <OptGroup key={group.toUpperCase()} label={group.toUpperCase()}>
      { ItemPropertyOptions[group as keyof typeof ItemPropertyOptions].map((itemProp) => {
        return <Option key={itemProp.name} value={itemProp.name}>{itemProp.name}</Option>
      })}
    </OptGroup>
  );
})

type SingleItemPropertyProps = {
  property: ItemProperty,
  onChange: (value: ItemProperty) => void
  onDelete?: () => void
}

function SingleItemProperty({property, onChange, onDelete}: SingleItemPropertyProps) {

  const updateName = (name: string) => {
    onChange(Object.assign(property, {name: name, value: undefined}))
  }

  const updateValue = (value: any) => {
    onChange(Object.assign(property, {value: value}))
  }

  let spec = null;
  let input = null;
  if (property.name) {
    spec = ItemPropertiesByName[property.name]

    if (spec.type === 'boolean') {
      input = <Switch
        checked={property.value}
        onChange={updateValue}
      />
    } else if (spec.type === 'integer') {
      input = <InputInteger
        value={property.value}
        addonAfter={spec.unit}
        onChange={updateValue}/>
    } else if (spec.type === 'float') {
      input = <InputFloat
        value={property.value}
        addonAfter={spec.unit}
        onChange={updateValue}/>
    }
  }

  let icon = null;

  if (property.name !== undefined) {
    if (property.value !== undefined) {
      icon = <CheckCircleOutlined style={{color:'#73d13d'}} />;
    } else {
      icon = (
        <Popover content='Value not set - will be ignored'>
          <ExclamationCircleOutlined style={{color:'#fa8c16'}} />
        </Popover>
      );
    }
  }

  return (
    <Row gutter={[10, 10]} style={{width:'100%'}}>

      <Col span={1}>{icon}</Col>

      <Col flex='none'>
        <Select
          onChange={updateName}
          defaultValue={undefined}
          value={property.name}
          style={{width:'220px'}}
          placeholder='Property'>
          {itemPropertyOptions}
        </Select>
      </Col>

      <Col flex='auto'>{input}</Col>

      { onDelete &&
        <Col span={2} flex='none'>
          <Button onClick={onDelete} style={{float:'right'}}>
            <DeleteOutlined />
          </Button>
        </Col>
      }

    </Row>
  );
}

type ItemPropertiesWeaponProps = {
  itemProperties: ItemProperties
  onChange: (value: ItemProperties) => void
  onDelete: () => void
}
function ItemPropertiesWeapon({ itemProperties, onChange, onDelete }: ItemPropertiesWeaponProps) {
  const setClazz = (clazz: PlayerClass) => {
    onChange(Object.assign(itemProperties, {playerClass: clazz, weapon: undefined}))
  }

  const setWeapon = (value: string) => {
    onChange(Object.assign(itemProperties, {weapon: value}))
  }

  const updateItemProperty = (idx: number, value: ItemProperty) => {    
    const properties = itemProperties.properties || []
    properties[idx] = value;
    onChange(Object.assign(itemProperties, {properties: properties}))
  }

  const deleteProperty = (idx: number) => {
    const properties = itemProperties.properties || []
    properties.splice(idx, 1)
    onChange(Object.assign(itemProperties, {properties: properties}))
  }
   
  const propertyList = itemProperties.properties || []
  // if the properties are empty or all propertis have a name set, show a new one
  if (
    (itemProperties.properties === undefined) || 
    (itemProperties.properties.length === 0) ||
    itemProperties.properties?.every(p => p.name !== undefined)
  ) {
    propertyList.push({})
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
    
    {!weaponSelected(itemProperties) && 
      <Hint text='Select a weapon to modify'/>
    }

    <Space direction='vertical' style={{width:'100%'}}>
    { weaponSelected(itemProperties)  &&
      
      propertyList.map((property, idx) => {
        return <SingleItemProperty
          property={property}
          onChange={value => updateItemProperty(idx, value)}
          onDelete={(idx === propertyList.length - 1)? undefined : (() => deleteProperty(idx))}/>
      })
      
    }

    </Space>
  </Card>);
}


type ItemPropertiesListProps = {
  config: GameServerConfig
  updateCallbacks: UpdateCallbacks
}

export function ItemPropertiesList({ config, updateCallbacks }: ItemPropertiesListProps) {

  const [itemProperties, setItemProperties] = useState(config.itemProperties || [])
  // const [state, setState] = useState<ItemPropertiesListState>({
  //   itemProperties: []
  // })

  // const itemProperties = config.itemProperties || []
  const updateConfig = (updated: ItemProperties[]) => {
    setItemProperties(updated)
    
    const sanitized = updated
      // filter out any weapons where the class/weapon are not set
      .filter(item =>  
        (item.playerClass !== undefined &&
          item.weapon !== undefined))
      // remove any item properties which are incomplete (name or value not set)
      .map(item => {
        const properties = item.properties || []
        return {
          playerClass: item.playerClass,
          weapon: item.weapon,
          properties: properties.filter(p => p.name !== undefined && p.value !== undefined)
        }
      })
      // remove any weapons which have no completed item properties
      .filter(item =>item.properties !== undefined && item.properties.length > 0)
      
    console.log(JSON.stringify(sanitized, null, 2))
    updateCallbacks.update('itemProperties')(sanitized)
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
                onChange={(value) => updateWeapon(idx, value)}
                onDelete={() => removeWeapon(idx)}/>
            </List.Item>);
        })}
      </List>
      <Button onClick={addWeapon}><PlusCircleOutlined /> Add Weapon to Modify</Button>
    </div>
  );
}