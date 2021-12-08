import { CheckCircleOutlined, DeleteOutlined, ExclamationCircleOutlined, QuestionCircleOutlined } from "@ant-design/icons";
import { Button, Col, Popover, Row, Select, Space, Switch} from "antd";
import { useState } from "react";
import {  ModProperty } from "../../api";
import { ModPropertySpecSet } from "../../data";
import { InputFloat, InputInteger } from "./Inputs";


type ModPropertyListItemProps = {
  property: ModProperty,
  specSet: ModPropertySpecSet
  onChange: (value: ModProperty) => void
  onDelete?: () => void
}

function ModPropertyListItem({property, specSet, onChange, onDelete}: ModPropertyListItemProps) {

  // if the weapon is updated, reset the properties
  const updateName = (name: string) => onChange(Object.assign(property, {name: name, value: undefined}));
  const updateValue = (value: any) => onChange(Object.assign(property, {value: value}));

  let spec = null;
  let input = null;
  if (property.name) {
    spec = specSet.byName[property.name]
    let help = null;
    if (spec.description) {
      help = (
        <Popover content={spec.description}>
          <QuestionCircleOutlined />
        </Popover>
      )
    }

    if (spec.type === 'boolean') {
      input = (
        <>
          {/* padding from .ant-input-number-group-addon to match input fields' help icon*/}
          <span style={{padding: '0 11px'}}>{help}</span>
          <Switch checked={property.value} onChange={updateValue}/>
        </>
      )
    } else if (spec.type === 'integer') {
      input = <InputInteger
        addonBefore={help}
        value={property.value}
        addonAfter={spec.unit}
        onChange={updateValue}/>
    } else if (spec.type === 'float') {
      input = <InputFloat
        addonBefore={help}
        value={property.value}
        addonAfter={spec.unit}
        onChange={updateValue}/>
    }
  }

  let icon = null;

  if (property.name != undefined) {
    if (property.value != undefined) {
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
          {specSet.groupedOptions}
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


type ModPropertyListProps = {
  properties?: ModProperty[]
  specSet: ModPropertySpecSet
  onChange: (properties: ModProperty[]) => void
}
export default function ModPropertyList(props: ModPropertyListProps) {

  //const propertyList = props.properties || []
  const [properties, setProperties] = useState(props.properties || [])

  const updateProperty = (idx: number, value: ModProperty) => { 
    properties[idx] = value;
    setProperties(properties)
    props.onChange(properties)
  }

  const deleteProperty = (idx: number) => {
    properties.splice(idx, 1);
    setProperties(properties)
    props.onChange(properties);
  }

  // if the properties are empty or all propertis have a name set, show a new one
  if (
    properties.length === 0 ||
    properties?.every(p => p.name !== undefined)
  ) {
    properties.push({})
  }

  return (
    <Space direction='vertical' style={{width:'100%'}}>
      {
        properties.map((property, idx) => {
          return <ModPropertyListItem
            key={idx}
            property={property}
            specSet={props.specSet}
            onChange={value => updateProperty(idx, value)}
            onDelete={(idx === properties.length - 1)? undefined : (() => deleteProperty(idx))}/>
        })
      }
    </Space>
  )
};