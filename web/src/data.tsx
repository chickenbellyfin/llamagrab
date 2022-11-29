import { Select } from 'antd'
import ClassPropertyOptions from '../../resources/class_properties.json'
import ItemPropertyOptions from '../../resources/item_properties.json'
import VehiclePropertyOptions from '../../resources/vehicle_properties.json'
import VehicleWeaponPropertyOptions from '../../resources/vehicle_weapon_properties.json'
import Maps from '../../resources/maps.json'
import ValueModOptions from '../../resources/value_mods.json'
import Weapons from '../../resources/weapons.json'


const { Option, OptGroup } = Select;

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


function weaponOptions(clazz: PlayerClass, groups?: string[]) {
  return Object.keys(WeaponsGrouped[clazz])
    .filter(group => groups? groups.includes(group) : true)
    .map(group => {
      return (
        <OptGroup key={group.toUpperCase()} label={group.toUpperCase()}>
          { WeaponsGrouped[clazz][group].map(weapon => {
            return <Option key={weapon.key} value={weapon.key}>{weapon.name}</Option>
          })}
        </OptGroup>
      );
  });
}

export type ModPropertySpec = {
  name: string,
  type: string,
  restrictions?: string,
  unit?: string,
  description?: string
}

// used by ModPropertyList.tsx to show options & look up values
export type ModPropertySpecSet = {
  byName: {[key: string]: ModPropertySpec}
  groupedOptions: JSX.Element[]
}

function createModPropertyOptions(options: {[key: string]: ModPropertySpec[]}): JSX.Element[]  {
  return Object.keys(options).map((group) => {
    return (
      <OptGroup key={group.toUpperCase()} label={group.toUpperCase()}>
        { options[group as keyof typeof options].map((itemProp) => {
          return <Option key={itemProp.name} value={itemProp.name}>{itemProp.name}</Option>
        })}
      </OptGroup>
    );
  })
}

const ItemPropertiesByName = Object.keys(ItemPropertyOptions).reduce((prev, group) => {
  const props = ItemPropertyOptions[group as keyof typeof ItemPropertyOptions]
  props.forEach(prop => Object.assign(prev, {[prop.name]: prop}))
  return prev;
}, {} as {[key: string]: ModPropertySpec})

const ClassPropertiesByName = Object.keys(ClassPropertyOptions).reduce((prev, group) => {
  const props = ClassPropertyOptions[group as keyof typeof ClassPropertyOptions]
  props.forEach(prop => Object.assign(prev, {[prop.name]: prop}))
  return prev;
}, {} as {[key: string]: ModPropertySpec})

const ValueModsByName = Object.keys(ValueModOptions).reduce((prev, group) => {
  const props = ValueModOptions[group as keyof typeof ValueModOptions]
  props.forEach(prop => Object.assign(prev, {[prop.name]: prop}))
  return prev;
}, {} as {[key: string]: ModPropertySpec})

const VehiclePropertiesByName = Object.keys(VehiclePropertyOptions).reduce((prev, group) => {
  const props = VehiclePropertyOptions[group as keyof typeof VehiclePropertyOptions]
  props.forEach(prop => Object.assign(prev, {[prop.name]: prop}))
  return prev;
}, {} as {[key: string]: ModPropertySpec})

const VehicleWeaponPropertiesByName = Object.keys(VehicleWeaponPropertyOptions).reduce((prev, group) => {
  const props = VehicleWeaponPropertyOptions[group as keyof typeof VehicleWeaponPropertyOptions]
  props.forEach(prop => Object.assign(prev, {[prop.name]: prop}))
  return prev;
}, {} as {[key: string]: ModPropertySpec})

const ItemPropertiesSpecSet: ModPropertySpecSet = {
  byName: ItemPropertiesByName,
  groupedOptions: createModPropertyOptions(ItemPropertyOptions)
}

const ClassPropertiesSpecSet: ModPropertySpecSet = {
  byName: ClassPropertiesByName,
  groupedOptions: createModPropertyOptions(ClassPropertyOptions)
}

const ValueModsSpecSet: ModPropertySpecSet = {
  byName: ValueModsByName,
  groupedOptions: createModPropertyOptions(ValueModOptions)
}

const VehiclePropertiesSpecSet: ModPropertySpecSet = {
  byName: VehiclePropertiesByName,
  groupedOptions: createModPropertyOptions(VehiclePropertyOptions)
}

const VehicleWeaponPropertiesSpecSet: ModPropertySpecSet = {
  byName: VehicleWeaponPropertiesByName,
  groupedOptions: createModPropertyOptions(VehicleWeaponPropertyOptions)
}

export {
  Maps,
  MapsByKey,
  getMaps,
  WeaponsGrouped,
  weaponOptions,
  ItemPropertiesSpecSet,
  ClassPropertiesSpecSet,
  ValueModsSpecSet,
  VehiclePropertiesSpecSet,
  VehicleWeaponPropertiesSpecSet
}
