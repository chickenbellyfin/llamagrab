import Maps from '../../common/maps.json'
import Weapons from '../../common/weapons.json'
import ItemPropertyOptions from '../../common/item_properties.json'
import { Select } from 'antd';


const { Option, OptGroup } = Select;

type Map = {
  key: string,
  name: string,
  lua: string,
  isCustom?: boolean
}

export type Weapon = {
  key: string,
  name: string,
  type: string
}


export type PlayerClass = 'Light' | 'Medium' | 'Heavy'

function getMaps(
  gameModes: string[] | undefined = undefined,
  includeCustom: boolean | undefined = false,
  includeBuiltIn: boolean | undefined = true): Array<string> {
  return Maps.filter(map => {
    if (gameModes && !gameModes.includes(map.gameMode)) {
      return false
    }

    if (!includeCustom && Boolean(map.isCustom)) {
      return false
    }

    if (!includeBuiltIn && !Boolean(map.isCustom)) {
      return false
    }
    return true;
  }).map(map => map.key)
}

const MapsByKey = Maps.map(map => {
  return {[map.key]: map}
}).reduce((l, r) => Object.assign(l, r), {})


function groupByType(weapons: Array<Weapon>): {[key: string]: Array<Weapon>} {
  return weapons.reduce((groups, item) => {
    const group = groups[item.type] || []
    group.push(item);
    groups[item.type] = group
    return groups
  }, {} as {[key: string]: Array<Weapon>})
}

const WeaponsGrouped = {
  'Light': groupByType(Weapons['Light']),
  'Medium': groupByType(Weapons['Medium']),
  'Heavy': groupByType(Weapons['Heavy']),
}


function weaponOptions(clazz: PlayerClass) {
  return Object.keys(WeaponsGrouped[clazz]).map(group => {
    return (
      <OptGroup key={group.toUpperCase()} label={group.toUpperCase()}>
        { WeaponsGrouped[clazz][group].map(weapon => {
          return <Option key={weapon.key} value={weapon.key}>{weapon.name}</Option>
        })}
      </OptGroup>
    );
  });
}

type ItemPropertySpec = {
  name: string,
  type: string,
  restrictions?: string,
  unit?: string,
  description?: string
}

const ItemPropertiesByName = Object.keys(ItemPropertyOptions).reduce((prev, group) => {
  const props = ItemPropertyOptions[group as keyof typeof ItemPropertyOptions]
  props.forEach(prop => Object.assign(prev, {[prop.name]: prop}))
  return prev;
}, {} as {[key: string]: ItemPropertySpec})


export {
  Maps,
  MapsByKey,
  getMaps,
  WeaponsGrouped,
  weaponOptions,
  ItemPropertyOptions,
  ItemPropertiesByName
}