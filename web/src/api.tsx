import { getToken } from './auth'


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

export type ServerStatus = {
  id: number,
  owner: string,
  name: string,
  region: string,
  regionName: string,
  status: string,
  gameMode: string,
  isPrivate: boolean
}

export type ServerSettings = {
  region?: string
  editors?: number[]
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
}

export type ServerVersion = {
  serverId: number
  serverConfig: string,
  numChanges: number,
  createdAt: number,
  createdBy: string
}

function removeEmptyModProperties(items: ModProperty[] | undefined): ModProperty[] | undefined {
  // NOTE: do not change to `!=`, needs to also check for null
  return items != undefined
    ? items.filter(item => item.name !== undefined && item.value !== undefined)
    : undefined;
}

function sanitizeGameServerConfig(config: GameServerConfig): GameServerConfig {
  const sanitized = Object.assign({}, config);

  if (sanitized.itemProperties) {
    sanitized.itemProperties = sanitized.itemProperties
      // filter out any weapons where the class/weapon are not set
      .filter(item => (item.playerClass !== undefined && item.weapon !== undefined))
      // remove any item properties which are incomplete (name or value not set)
      .map(item =>  Object.assign(item, {properties: removeEmptyModProperties(item.properties)}))
      // remove any weapons which have no completed item properties
      .filter(item =>item.properties !== undefined && item.properties.length > 0)
  }

  if (sanitized.itemValueMods) {
    sanitized.itemValueMods = sanitized.itemValueMods
      // filter out any weapons where the class/weapon are not set
      .filter(item => (item.playerClass !== undefined && item.weapon !== undefined))
      // remove any item properties which are incomplete (name or value not set)
      .map(item =>  Object.assign(item, {properties: removeEmptyModProperties(item.properties)}))
      // remove any weapons which have no completed item properties
      .filter(item =>item.properties !== undefined && item.properties.length > 0)
  }

  sanitized.lightClassProperties = removeEmptyModProperties(sanitized.lightClassProperties)
  sanitized.mediumClassProperties = removeEmptyModProperties(sanitized.mediumClassProperties)
  sanitized.heavyClassProperties = removeEmptyModProperties(sanitized.heavyClassProperties)
  sanitized.lightValueMods = removeEmptyModProperties(sanitized.lightValueMods)
  sanitized.mediumValueMods = removeEmptyModProperties(sanitized.mediumValueMods)
  sanitized.heavyValueMods = removeEmptyModProperties(sanitized.heavyValueMods)

  if (sanitized.mutualExclusions) {
    sanitized.mutualExclusions = sanitized.mutualExclusions.filter(item => {
      return item.playerClass !== undefined &&
        item.item1 !== undefined &&
        item.item2 !== undefined &&
        item.item1 != item.item2
    });
  }

  if (sanitized.password === '') {
    sanitized.password = undefined;
  }
  return sanitized;
}

export type LoginRequest = {
  username: string,
  password: string
}

export type AccountCreateRequest = LoginRequest

type UpdatePasswordRequest = {
  currentPassword: string,
  newPassword: string
}

interface RequestArgs {
  path: string,
  method?: string,
  headers?: {[key: string]: string},
  body?: string
  includeAuthToken?: boolean
};

function handleApiError<T>(response: Response): Promise<T> {
  return response.json()
  .catch((jsonError: Error) => {
    throw Error('Unknown Error')
  })
  .then(data => {
    const details = data.detail
    if (typeof details === 'string') {
      throw Error(details)
    } else if (typeof details === 'object') {
      throw Error(details[0]['msg'])
    } else {
      throw Error('Unknown Error')
    }
  })

}

async function doRequest<T>({path, method, headers, body, includeAuthToken = true}: RequestArgs): Promise<T> {
  if (body && !headers) {
    headers = { 'Content-Type': 'application/json' }
  }
  const authHeader = includeAuthToken && { 'Authorization': `Bearer ${getToken()}` };

  return fetch(path, {
    method: method || 'GET',
    headers: {...authHeader, ...headers},
    body: body
  })
    .catch((error: Error) => {
      // fetch only throws on network error
      throw Error('Unable to connect')
    })
    .then(response => {
      if (response.ok) {
        return response.json() as Promise<T>;
      } else {
        return handleApiError(response)
      }
    })
};

async function getUser(): Promise<UserAccount> {
  return doRequest({
    path: '/api/account/user'
  })
}

async function getAllUserAccounts(): Promise<Array<UserAccount>> {
  return doRequest({
    path: '/api/accounts'
  })
}

async function getAllUsers(): Promise<User[]> {
  return doRequest({
    path: '/api/users'
  })
}

async function createUser(request: AccountCreateRequest): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/account/create',
    body: JSON.stringify(request),
    includeAuthToken: false
  })
}

async function deleteUser(userId: number): Promise<any> {
  return doRequest({
    method: 'DELETE',
    path: `/api/account/${userId}`
  })
}

async function changePassword(request: UpdatePasswordRequest): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/account/change_password',
    body: JSON.stringify(request)
  })
}

async function setTribesUsername(name: string): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/account/set_tribes_name',
    body: JSON.stringify({tribesUsername: name})
  })
}

async function getUserServerList(): Promise<Array<ServerStatus>> {
  return doRequest({
    path: '/api/servers/user'
  })
}

async function getSharedServerList(): Promise<Array<ServerStatus>> {
  return doRequest({
    path: '/api/servers/shared'
  })
}

async function getAllServerList(): Promise<Array<ServerStatus>> {
  return doRequest({
    path: '/api/servers/all'
  })
}


async function getServerStatus(serverId: number): Promise<ServerStatus> {
  return doRequest({
    path: `/api/server/${ serverId }/status`
  });
}

async function getServerSettings(serverId: number): Promise<ServerSettings> {
  return doRequest({
    path: `/api/server/${ serverId }/settings`
  })
}

async function setServerSettings(serverId: number, settings: ServerSettings): Promise<any> {
  return doRequest({
    method: 'POST',
    path: `/api/server/${ serverId }/settings`,
    body: JSON.stringify(settings)
  })
}

async function createServer(serverConfig: GameServerConfig, serverSettings: ServerSettings): Promise<any> {
  return doRequest({
    method: 'PUT',
    path: '/api/servers',
    body: JSON.stringify({
      serverConfig: sanitizeGameServerConfig(serverConfig),
      serverSettings: serverSettings
    })
  })
}

async function getServerConfig(serverId: number): Promise<GameServerConfig> {
  return doRequest({
    path: `/api/server/${serverId}/config`
  })
}

async function setServerConfig(serverId: number, serverConfig: GameServerConfig): Promise<any> {
  return doRequest({
    method: 'POST',
    path: `/api/server/${serverId}/config`,
    body: JSON.stringify(sanitizeGameServerConfig(serverConfig))
  })
}


async function startServer(serverId: number): Promise<any> {
  return doRequest({
    method: 'POST',
    path: `/api/server/${serverId}/start`
  })
}

async function stopServer(serverId: number): Promise<any> {
  return doRequest({
    method: 'POST',
    path: `/api/server/${serverId}/stop`
  })
}

async function deleteServer(serverId: number): Promise<any> {
  return doRequest({
    method: 'DELETE',
    path: `/api/server/${serverId}`
  })
}

async function getServerVersions(serverId: number): Promise<ServerVersion[]> {
  return doRequest({
    path: `/api/server/${serverId}/history`
  })
}

async function verifyUser(userId: number): Promise<any> {
  return doRequest({
    method: 'POST',
    path: `/api/admin/verify_user/${userId}`
  })
}

async function makeAdmin(userId: number): Promise<any> {
  return doRequest({
    method: 'POST',
    path: `/api/admin/make_admin/${userId}`
  })
}

async function removeAdmin(userId: number): Promise<any> {
  return doRequest({
    method: 'DELETE',
    path: `/api/admin/make_admin/${userId}`
  })
}

async function getRegions(): Promise<{[key: string]: string}> {
  return doRequest({
    path: '/api/data/regions'
  })
}


export const API = {
  Account: {
    getUser,
    createUser,
    changePassword,
    setTribesUsername,
    getAllUserAccounts,
    getAllUsers,
    deleteUser,
  },
  Admin: {
    verifyUser,
    makeAdmin,
    removeAdmin,
  },
  Server: {
    getServerStatus,
    getUserServerList,
    getSharedServerList,
    getAllServerList,
    createServer,
    getServerSettings,
    setServerSettings,
    getServerConfig,
    setServerConfig,
    startServer,
    stopServer,
    deleteServer,
    getServerVersions
  },
  Data: {
    getRegions
  }
}