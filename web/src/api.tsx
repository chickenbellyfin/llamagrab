import {BASE_URL} from './config'
import { getToken } from './auth' 


export type UserLimits = {
  serverLimit: number,
  activeLimit: number,
  serverCount: number
}

export type User = {
  id: number,
  username: string,
  tier: string,
  limits: UserLimits,
  tribesUsername?: string
}

export type ServerStatus = {
  id: number,
  owner: string,
  name: string,
  region: string,
  regionName: string,
  status: string,
  gameMode: string,
  serverconfig: any
}

export type ServerSettings = {
  region?: string
}

export type ItemProperty = {
  name?: string,
  value?: any
}

export type ItemProperties = {
  playerClass?: string,
  weapon?: string,
  properties?: ItemProperty[]
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

  return fetch(BASE_URL + path, {
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

async function getUser(): Promise<User> {
  return doRequest({
    path: '/api/account/user'
  })
}

async function getAllUsers(): Promise<Array<User>> {
  return doRequest({
    path: '/api/accounts'
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

async function getServerList(): Promise<Array<ServerStatus>> {
  return doRequest({
    path: '/api/servers'
  })
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
      serverConfig: serverConfig,
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
    body: JSON.stringify(serverConfig)
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
    getAllUsers
  },
  Admin: {
    verifyUser,
    makeAdmin,
    removeAdmin,
  },
  Server: {
    getServerList,
    createServer,
    getServerSettings,
    setServerSettings,
    getServerConfig,
    setServerConfig,
    startServer,
    stopServer,
    deleteServer
  },
  Data: {
    getRegions
  }
}