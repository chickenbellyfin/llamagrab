import Maps from '../../common/maps.json'

type Map = {
  key: string,
  name: string,
  lua: string,
  isCustom?: boolean
}

function getMaps(
  gameMode: string | undefined = undefined,
  includeCustom: boolean | undefined = false): Array<string> {
  return Maps.filter(map => {
    if (gameMode && map.gameMode !== gameMode) {
      return false
    }

    if (!includeCustom && map.isCustom) {
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