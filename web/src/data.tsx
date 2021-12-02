import Maps from '../../common/maps.json'
import Weapons from '../../common/weapons.json'

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

export {
  Maps,
  MapsByKey,
  getMaps,
  WeaponsGrouped
}