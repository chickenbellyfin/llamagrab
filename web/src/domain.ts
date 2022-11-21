
export type UserLimits = {
  serverLimit: number,
  activeLimit: number,
  serverCount: number
}

export type UserAccount = {
  id: number,
  username: string,
  tier: string,
  limits: UserLimits,
  tribesUsername?: string
}

export type User = {
  id: number,
  username: string
}

export type Status = 'running' | 'restarting' | 'starting' | 'stopping' | 'offline' | 'unknown';

export type ServerStatus = {
  id: number,
  owner: string,
  name: string,
  region: string,
  regionName: string,
  enabled: boolean,
  status: Status,
  game: GameType
  isPrivate: boolean
}

export type RegionStatus = {
  region: string,
  online: boolean,
  servers: ServerStatus[]
}

export type GameType = 'tribes_ascend_ootb' | 'tribes_ascend_goty'

export type ServerSettings = {
  region?: string
  editors?: number[]
  game: GameType
}

export type ModProperty = {
  name?: string,
  value?: any
}

export type ItemProperties = {
  playerClass?: string,
  weapon?: string,
  properties?: ModProperty[]
}

export type VehicleWeaponProperties = {
  vehicleWeapon?: string,
  properties?: ModProperty[]
}

export type MutualExclusion = {
  playerClass?: string,
  item1?: string,
  item2?: string
}

export type HardcodedLoadout = {
  primary?: string
  secondary?: string
  tertiary?: string
  belt?: string
  pack?: string
}

export type GameServerConfig = {
  displayName: string
  description: string
  password?: string
  admins?: string[]

  teamAssignType: string
  autoBalance: boolean
  timeLimit?: number
  overtimeLimit?: number
  respawnTime?: number
  sniperRespawnDelay?: number
  ammoPickupLifespan?: number
  ctfFlagTimeout?: number
  warmupTime?: number

  ctfCapLimit?: number
  tdmKillLimit?: number
  arenaRounds?: number
  arenaLives?: number
  rabbitScoreLimit?: number
  cahScoreLimit?: number
  ctfBlitzAllFlagsMove?: boolean

  energyMultiplier?: number

  flagDragLight?: number
  flagDragMedium?: number
  flagDragHeavy?: number
  flagDragDeceleration?: number

  maxPlayers?: number
  nakedSpawn?: boolean
  lightCountLimit?: number
  mediumCountLimit?: number
  heavyCountLimit?: number

  friendlyFireMultiplier?: number

  friendlyFire?: boolean
  mapVoting?: boolean
  maps: Array<string> | []

  vehicleHealthMultiplier?: number
  gravCycleLimit?: number
  shrikeLimit?: number
  beowulfLimit?: number
  gravCycleSpawnTime?: number
  shrikeSpawnTime?: number
  beowulfSpawnTime?: number

  lightWeaponBans: Array<string>
  mediumWeaponBans: Array<string>
  heavyWeaponBans: Array<string>

  itemProperties?: Array<ItemProperties>
  lightClassProperties?: ModProperty[]
  mediumClassProperties?: ModProperty[]
  heavyClassProperties?: ModProperty[]

  forceHardcodedLoadouts?: boolean
  lightHardcodedLoadouts?: HardcodedLoadout[]
  mediumHardcodedLoadouts?: HardcodedLoadout[]
  heavyHardcodedLoadouts?: HardcodedLoadout[]

  lightDisabledEquipPoints?: string[]
  mediumDisabledEquipPoints?: string[]
  heavyDisabledEquipPoints?: string[]

  lightValueMods?: ModProperty[]
  mediumValueMods?: ModProperty[]
  heavyValueMods?: ModProperty[]
  itemValueMods?: ItemProperties[]

  mutualExclusions?: MutualExclusion[]

  gravCycleProperties?: ModProperty[]
  shrikeProperties?: ModProperty[]
  beowulfProperties?: ModProperty[]

  vehicleWeaponProperties?: VehicleWeaponProperties[]
}

export type ServerVersion = {
  versionId: number
  serverId: number
  serverConfig: string
  numChanges: number
  createdAt: number
  createdBy: string
}

export type ServerVersionChange = {
  field: string,
  old: string | any[]
  new: string | any[]
}
export type ServerVersionDetails = {
  changes: ServerVersionChange[]
}
