import { getToken } from './auth';
import { GameServerConfig, IPBan, IPLogEntry, Loginserver, ModProperty, RegionStatus, ServerSettings, ServerStatus, ServerVersion, ServerVersionDetails, User, UserAccount } from './domain';

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

  if (sanitized.vehicleWeaponProperties) {
    sanitized.vehicleWeaponProperties = sanitized.vehicleWeaponProperties
      // filter out any vehicle weapons where the weapon is not set
      .filter(item => (item.vehicleWeapon !== undefined))
      // remove any item properties which are incomplete (name or value not set)
      .map(item =>  Object.assign(item, {properties: removeEmptyModProperties(item.properties)}))
      // remove any vehicle weapons which have no completed item properties
      .filter(item =>item.properties !== undefined && item.properties.length > 0)
  }

  sanitized.lightClassProperties = removeEmptyModProperties(sanitized.lightClassProperties)
  sanitized.mediumClassProperties = removeEmptyModProperties(sanitized.mediumClassProperties)
  sanitized.heavyClassProperties = removeEmptyModProperties(sanitized.heavyClassProperties)
  sanitized.lightValueMods = removeEmptyModProperties(sanitized.lightValueMods)
  sanitized.mediumValueMods = removeEmptyModProperties(sanitized.mediumValueMods)
  sanitized.heavyValueMods = removeEmptyModProperties(sanitized.heavyValueMods)
  sanitized.gravCycleProperties = removeEmptyModProperties(sanitized.gravCycleProperties)
  sanitized.shrikeProperties = removeEmptyModProperties(sanitized.shrikeProperties)
  sanitized.beowulfProperties = removeEmptyModProperties(sanitized.beowulfProperties)

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

async function getRegionStatus(): Promise<RegionStatus[]> {
  return doRequest({
    path: '/api/servers/region_status'
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

async function restartServer(serverId: number): Promise<any> {
  return doRequest({
    method: 'POST',
    path: `/api/server/${serverId}/restart`
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

async function getServerVersionDetails(serverId: number, versionId: number): Promise<ServerVersionDetails[]> {
  return doRequest({
    path: `/api/server/${serverId}/history/${versionId}`
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

async function setSiteFlag(key: string, value: any): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/admin/site/flag',
    body: JSON.stringify({
      'key': key,
      'value': value
    })
  })
}

async function getSiteFlags(): Promise<any> {
  return doRequest({
    path: '/api/admin/site/flags'
  })
}

async function requestSync(): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/admin/site/request_sync'
  })
}

async function restartAllServers(region: string | undefined = undefined): Promise<number> {
  
  return doRequest({
    method: 'POST',
    path: region ? `/api/admin/site/restart_all/${region}` : '/api/admin/site/restart_all'
  })
}

async function disableAllServers(region: string | undefined = undefined): Promise<number> {
  return doRequest({
    method: 'POST',
    path: region ? `/api/admin/site/disable_all/${region}` : '/api/admin/site/disable_all'
  })
}

async function getLoginservers(): Promise<Loginserver[]> {
  return doRequest({
    path: '/api/data/loginservers'
  })
}

async function getIPLogs(): Promise<IPLogEntry[]> {
  return doRequest({
    path: '/api/admin/ip/log'
  })
}

async function fetchIPLogs(): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/admin/ip/fetch'
  })
}

async function getIPBans(): Promise<IPBan[]> {
  return doRequest({
    path: '/api/admin/ip/bans'
  })
}

async function createIPBan(ip: string, reason: string): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/admin/ip/ban',
    body: JSON.stringify({ip, reason})
  })
}

async function removeIPBan(id: number): Promise<any> {
  return doRequest({
    method: 'DELETE',
    path: `/api/admin/ip/ban/${id}`
  })
}

async function pushBanlist(): Promise<any> {
  return doRequest({
    method: 'POST',
    path: '/api/admin/ip/push_banlist',
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
    Site: {
      setSiteFlag,
      getSiteFlags,
      requestSync,
      restartAllServers,
      disableAllServers
    },
    getIPLogs,
    fetchIPLogs,
    getIPBans,
    createIPBan,
    removeIPBan,
    pushBanlist
  },
  Server: {
    getServerStatus,
    getUserServerList,
    getSharedServerList,
    getAllServerList,
    getRegionStatus,
    createServer,
    getServerSettings,
    setServerSettings,
    getServerConfig,
    setServerConfig,
    startServer,
    stopServer,
    restartServer,
    deleteServer,
    getServerVersions,
    getServerVersionDetails
  },
  Data: {
    getRegions,
    getLoginservers
  }
}
