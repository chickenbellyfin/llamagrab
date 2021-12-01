import { Button, Form, Popconfirm, Radio, RadioChangeEvent, Select, Space, Switch} from "antd"
import { LabeledValue } from "antd/lib/select";
import { useState } from "react"

import { getMaps, MapsByKey } from "../../data";


const { Option } = Select;

type MapSelectorProps = {
  gameTypes: Array<string>,
  mapList: Array<string>,
  onChange: (maps: Array<string>) => void
}

type MapSelectorState = {
  gameTypes: Array<string>,
  maps: Array<string>
}

export default function MapSelector({gameTypes, mapList, onChange}: MapSelectorProps) {

  // If there is already a map list (existing server), start in select mode
  // if not, default to all maps
  let initialMapList = mapList.filter(m => gameTypes.includes( MapsByKey[m].gameMode))
  if (initialMapList.length === 0) {
    initialMapList = getMaps(gameTypes)
  }

  const [state, setState] = useState<MapSelectorState>({
    gameTypes: gameTypes,
    maps: initialMapList
  })

  // if game types changed, remove maps which are not part of the game types anymore
  if (state.gameTypes != gameTypes) {
    setState({
      gameTypes,
      maps: state.maps.filter(m => gameTypes.includes( MapsByKey[m].gameMode))
    });
  }
  
  const updateMapList = (newSelectedMaps: Array<string>) => {
    setState({
      gameTypes: state.gameTypes,
      maps: newSelectedMaps
    })
    onChange(newSelectedMaps)
  }

  const addMaps = (mapsToAdd: Array<string>) => {
    updateMapList(state.maps.concat(mapsToAdd))
  }

  const handleCustomMapListChange = (selected: Array<LabeledValue>) => {
    const selectedKeys = selected.map(v => v.value as string)
    console.log(`selected ${selectedKeys}`)
    updateMapList(selectedKeys)
  }

  const unSelectedMaps = getMaps(gameTypes, false)
    .filter(map => !state.maps.includes(map))

  const unSelectedCustomMaps = getMaps(gameTypes, true, false)
    .filter(map => !state.maps.includes(map))


  return (
    <>

      <Form.Item label='Select Maps'>
        <Select 
          size='large'
          mode='multiple'
          allowClear
          onChange={handleCustomMapListChange}
          value={state.maps.map(mapName => {
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
      <Form.Item label=' ' colon={false}>
        <Space>
        {unSelectedMaps.length > 0 &&
          <Button 
            disabled={!(unSelectedMaps.length > 0)}
            size='small'
            onClick={e => addMaps(unSelectedMaps)}>
              {`Add All (${unSelectedMaps.length} more)`}
          </Button>
        }
        {unSelectedCustomMaps.length > 0 &&
          <Popconfirm
            title='Players must have the custom maps installed'
            onConfirm={e => addMaps(unSelectedCustomMaps)}
            okText="Understood"
            >
          <Button 
            disabled={!(unSelectedCustomMaps.length > 0)}
            size='small'>
              {`Add (${unSelectedCustomMaps.length} custom maps)`}
          </Button>
          </Popconfirm>
        }
        </Space>
      </Form.Item>
      {/* <Form.Item 
        
        label={`Include Custom Maps`}>
        <Switch disabled={!allMaps}
          defaultChecked={false}
          checked={includeCustomMaps}
          onChange={handleIncludeCustomMaps}/>
      </Form.Item> */}
    </>
  )
}