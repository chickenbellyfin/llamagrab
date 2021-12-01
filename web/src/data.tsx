import Maps from '../../common/maps.json'

type Map = {
  key: string,
  name: string,
  lua: string,
  isCustom?: boolean
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

export {
  Maps,
  MapsByKey,
  getMaps
}