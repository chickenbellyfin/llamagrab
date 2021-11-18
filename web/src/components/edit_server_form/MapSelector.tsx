import { Form, Radio, RadioChangeEvent, Select, Switch} from "antd"
import { LabeledValue } from "antd/lib/select";
import { useState } from "react"

import { getMaps, MapsByKey } from "../../data";


const { Option } = Select;

type MapSelectorProps = {
  gameType: 'CTF',
  mapList: Array<string>,
  onChange: (maps: Array<string>) => void
}


export default function MapSelector({gameType, mapList, onChange}: MapSelectorProps) {
  
  // If there is already a map list (existing server), start in select mode
  // if not, default to all maps
  let initialMapList = mapList
  let initialAllMaps = false;
  if (initialMapList.length === 0) {
    initialMapList = getMaps(gameType)
    initialAllMaps = true
  }

  const [allMaps, setAllMaps] = useState(initialAllMaps)
  const [includeCustomMaps, setIncludeCustomMaps] = useState(false)
  const [selectedMaps, setSelectedMaps] = useState<Array<string>>(initialMapList)
  console.log(`allMaps = ${allMaps}`)
  
  const updateMapList = (
    newAllMaps: boolean,
    newIncludeCustomMaps: boolean,
    newSelectedMaps: Array<string>) => {
    if (newAllMaps) {
      var mapList = getMaps(gameType)
      if (newIncludeCustomMaps) {
        mapList = getMaps(gameType, true)
      }
      setSelectedMaps(mapList)
      onChange(mapList)
    } else {
      setSelectedMaps(newSelectedMaps)
      onChange(newSelectedMaps)
    }
  }
  

  const allMapsUpdated = (e: RadioChangeEvent) => {
    const value = e.target.value
    setAllMaps(value)
    
    if (!value) {
      setIncludeCustomMaps(false)
      updateMapList(value, false, selectedMaps)
    } else {
      updateMapList(value, includeCustomMaps, selectedMaps)
    }
  }

  const handleIncludeCustomMaps = (value: boolean) => {
    setIncludeCustomMaps(value)
    updateMapList(allMaps, value, selectedMaps)
  }

  const handleCustomMapListChange = (selected: Array<LabeledValue>) => {
    const selectedKeys = selected.map(v => v.value as string)
    console.log(`selected ${selectedKeys}`)
    updateMapList(allMaps, includeCustomMaps, selectedKeys)
  }

  const unSelectedMaps = getMaps(gameType, true)
    .filter(map => !selectedMaps.includes(map))

  return (
    <>
      <Form.Item
        label='Map List'>
        <Radio.Group value={allMaps} onChange={allMapsUpdated}>
          <Radio value={true}>All Maps</Radio>
          <Radio value={false}>Select...</Radio>
        </Radio.Group>
      </Form.Item>
      <Form.Item 
        
        label={`Include Custom Maps`}>
        <Switch disabled={!allMaps}
          defaultChecked={false}
          checked={includeCustomMaps}
          onChange={handleIncludeCustomMaps}/>
      </Form.Item>

      <Form.Item label='Select Maps'>
        <Select 
          size='large'
          mode='multiple'
          allowClear
          disabled={allMaps}
          onChange={handleCustomMapListChange}
          value={selectedMaps.map(mapName => {
            return {
              key: mapName,
              value: mapName,
              label: (
                <>
                  <small style={{opacity: '60%'}}>{MapsByKey[mapName].gameMode} </small>
                  {MapsByKey[mapName].name}
                </>
              )
            }
          })}
          labelInValue>
          {unSelectedMaps.map(mapName => {
            return (<Option key={mapName} value={mapName}>
              <small style={{opacity: '60%'}}>{MapsByKey[mapName].gameMode} </small>
              {MapsByKey[mapName].name}
              </Option>);
          })}
  
        </Select>
      </Form.Item>
    </>
  )
}