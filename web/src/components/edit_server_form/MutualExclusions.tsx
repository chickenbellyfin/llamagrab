import { CheckCircleOutlined, DeleteOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { Button, Col, Popover, Row, Select, Space } from "antd";
import { useState } from "react";
import { MutualExclusion } from "../../api";
import { ItemPropertiesSpecSet, PlayerClass, weaponOptions } from "../../data";

type MutualExclusionItemProps = {
  value: MutualExclusion,
  onChange: (value: MutualExclusion) => void
  onDelete?: () => void
}
function MutualExclusionItem(props: MutualExclusionItemProps) {

  const updateClass = (value: string) => 
    props.onChange(Object.assign(props.value, {playerClass: value, item1: undefined, item2: undefined}))
  const updateItem1 = (value: string) => props.onChange(Object.assign(props.value, {item1: value}))
  const updateItem2 = (value: string) => props.onChange(Object.assign(props.value, {item2: value}))

  let icon: JSX.Element | null = <CheckCircleOutlined style={{color:'#73d13d'}}/>;
  if (props.value.playerClass == undefined) {
    icon = null;
  } else if (props.value.item1 == undefined || props.value.item2 == undefined) {
    icon = (
      <Popover content='both items must be selected - will be ignored' >
        <ExclamationCircleOutlined style={{color:'#fa8c16'}} />
      </Popover>
    );
  } else if (props.value.item1 == props.value.item2) {
    icon = (
      <Popover content= 'items can not match - will be ignored'>
        <ExclamationCircleOutlined style={{color:'#fa8c16'}} />
      </Popover>
    );
  }


  return (
    <Row gutter={[10, 10]}>
      <Col span={1}>{icon}</Col>
      <Col>
        <Select
          style={{width: '100px'}}
          placeholder='Class'
          onChange={updateClass}
          value={props.value.playerClass as PlayerClass}
          options={[
          {key: "Light", label: "Light", value: "Light"},
          {key: "Medium", label: "Medium", value: "Medium"},
          {key: "Heavy", label: "Heavy", value: "Heavy"},
        ]}/>
      </Col>
      <Col >
      <Select
        style={{width: '200px'}}
        placeholder='Item 1'
        onChange={updateItem1}
        value={props.value.item1}
        disabled={props.value.playerClass === undefined}
        >
        { props.value.playerClass ? weaponOptions(props.value.playerClass as PlayerClass) : []}
      </Select>
      </Col>
      <Col>
      <Select
        style={{width: '200px'}}
        placeholder='Item 2'
        onChange={updateItem2}
        value={props.value.item2}
        disabled={props.value.playerClass === undefined}
        >
        { props.value.playerClass ? weaponOptions(props.value.playerClass as PlayerClass) : []}
      </Select>
      </Col>
      <Col>
      { props.onDelete &&
        <Button onClick={props.onDelete} style={{float:'right'}}>
              <DeleteOutlined />
        </Button>
      }
      </Col>
    </Row>
  );
}

type MutualExclusionListProps = {
  mutualExclusions?: MutualExclusion[]
  onChange: (value: MutualExclusion[]) => void
}
export default function MutualExclusionList(props: MutualExclusionListProps) {

  const [mutualExclusions, setMutualExclusions] = useState<MutualExclusion[]>(props.mutualExclusions || [])

  const updateItem = (idx: number, value: MutualExclusion) => {
    mutualExclusions[idx] = value;
    setMutualExclusions(mutualExclusions)
    props.onChange(mutualExclusions)
  }

  const deleteItem = (idx: number) => {
    mutualExclusions.splice(idx, 1);
    setMutualExclusions(mutualExclusions)
    props.onChange(mutualExclusions)
  }

  if (
    mutualExclusions.length === 0 ||
    mutualExclusions?.every(i => i.playerClass !== undefined)
  ) {
    mutualExclusions.push({})
  }

  return (
    <Space direction='vertical' style={{width: '100%'}}>
        { 
          mutualExclusions.map((item, idx) => 
            <MutualExclusionItem
              value={item}
              onChange={(value) => updateItem(idx, value)} 
              onDelete={idx == mutualExclusions.length -1 ? undefined : () => deleteItem(idx)}
            />
          )
        }
    </Space>
  );
}