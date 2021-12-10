ServerSettings.Description = "Test Server"
ServerSettings.Motd = "the description the description"
ServerSettings.GameSettingMode = ServerSettings.GameSettingModes.OOTB
ServerSettings.TeamAssignType = TeamAssignTypes.Unbalanced
ServerSettings.MaxPlayers = 28
ServerSettings.AutoBalanceTeams = false
ServerSettings.Password = "testpassword"
ServerSettings.TimeLimit = 44
ServerSettings.OvertimeLimit = 13
ServerSettings.WarmupTime = 54
ServerSettings.RespawnTime = 12
ServerSettings.SniperRespawnDelay = 2
ServerSettings.AmmoPickupLifespan = 99
ServerSettings.CTFFlagTimeout = 45
ServerSettings.FriendlyFire = true
ServerSettings.FriendlyFireMultiplier = 1.30
ServerSettings.NakedSpawn = true
ServerSettings.VehicleHealthMultiplier = 0.50
ServerSettings.GravCycleLimit = 4
ServerSettings.GravCycleSpawnTime = 40
ServerSettings.ShrikeLimit = 5
ServerSettings.ShrikeSpawnTime = 50
ServerSettings.BeowulfLimit = 6
ServerSettings.BeowulfSpawnTime = 60
ServerSettings.CTFCapLimit = 90
ServerSettings.TDMKillLimit = 91
ServerSettings.ArenaRounds = 92
ServerSettings.ArenaLives = 93
ServerSettings.RabbitScoreLimit = 94
ServerSettings.CaHScoreLimit = 95
ServerSettings.CTFBlitzAllFlagsMove = true
ServerSettings.EnergyMultiplier = 1.22
ServerSettings.FlagDragLight = 101
ServerSettings.FlagDragMedium = 102
ServerSettings.FlagDragHeavy = 103
ServerSettings.FlagDragDeceleration = 104
ServerSettings.MapRotation.VotingEnabled = true
ServerSettings.MapRotation.add(Maps.CTF.Katabatic)
ServerSettings.MapRotation.add(Maps.Arena.WalledIn)
ServerSettings.MapRotation.addCustom("TrCTF-Periculo")
ServerSettings.BannedItems.add("Light", "Bolt Launcher")
ServerSettings.BannedItems.add("Light", "Prism Mine")
ServerSettings.BannedItems.add("Medium", "NJ5-B SMG")
ServerSettings.BannedItems.add("Medium", "Cluster Grenade")
ServerSettings.BannedItems.add("Heavy", "Heavy Spinfusor")
ServerSettings.BannedItems.add("Heavy", "Fusion Mortar")

-- [hitscan.lua]
--------------------------------------------------------------------------------
ServerSettings.BannedItems.add("Light", "Sparrow")
ServerSettings.BannedItems.add("Light", "Phase Rifle")
ServerSettings.BannedItems.add("Light", "BXT1 Rifle")
ServerSettings.BannedItems.add("Light", "Shotgun")
ServerSettings.BannedItems.add("Medium", "Eagle Pistol")
ServerSettings.BannedItems.add("Medium", "Sawed-Off Shotgun")
ServerSettings.BannedItems.add("Heavy", "Nova Colt")
ServerSettings.BannedItems.add("Heavy", "Automatic Shotgun")

--------------------------------------------------------------------------------
Items.setProperty("Light", "Light Spinfusor", Items.Properties.Damage, 800.00)
Items.setProperty("Light", "Light Spinfusor", Items.Properties.CanZoom, true)
Items.setProperty("Heavy", "Heavy Bolt Launcher", Items.Properties.ShotEnergyCost, 10.00)
Items.setProperty("Heavy", "Heavy Bolt Launcher", Items.Properties.BurstShotCount, 3)
Classes.setProperty("Light", Classes.Properties.EnergyPool, 110.00)
Classes.setProperty("Light", Classes.Properties.MomentumDampeningEnabled, true)
Classes.setProperty("Medium", Classes.Properties.Mass, 5.00)
Classes.setProperty("Heavy", Classes.Properties.RegenTime, 15.00)
ServerSettings.ForceHardcodedLoadouts = true
Loadouts.Hardcoded.Light.set(0, Loadouts.EquipPoints.Primary, "Light Spinfusor")
Loadouts.Hardcoded.Light.set(0, Loadouts.EquipPoints.Belt, "Explosive Nitron")
Loadouts.Hardcoded.Light.set(1, Loadouts.EquipPoints.Pack, "Thrust Pack")
Loadouts.Hardcoded.Medium.set(0, Loadouts.EquipPoints.Primary, "Spinfusor")
Loadouts.Hardcoded.Medium.set(0, Loadouts.EquipPoints.Secondary, "Honorfusor")
Loadouts.Hardcoded.Medium.set(0, Loadouts.EquipPoints.Belt, "Anti-Personnel Grenade")
Loadouts.Hardcoded.Medium.set(0, Loadouts.EquipPoints.Pack, "Utility Pack")
Loadouts.Hardcoded.Medium.set(1, Loadouts.EquipPoints.Primary, "Spinfusor")
Loadouts.Hardcoded.Medium.set(1, Loadouts.EquipPoints.Secondary, "Honorfusor")
Loadouts.Hardcoded.Medium.set(1, Loadouts.EquipPoints.Belt, "Anti-Personnel Grenade")
Loadouts.Hardcoded.Medium.set(1, Loadouts.EquipPoints.Pack, "Utility Pack")
Loadouts.Hardcoded.Medium.set(2, Loadouts.EquipPoints.Primary, "Spinfusor")
Loadouts.Hardcoded.Medium.set(2, Loadouts.EquipPoints.Secondary, "Honorfusor")
Loadouts.Hardcoded.Medium.set(2, Loadouts.EquipPoints.Belt, "Anti-Personnel Grenade")
Loadouts.Hardcoded.Medium.set(2, Loadouts.EquipPoints.Pack, "Utility Pack")
Loadouts.Hardcoded.Heavy.set(2, Loadouts.EquipPoints.Tertiary, "Heavy Bolt Launcher")

-- [admin.lua]
--------------------------------------------------------------------------------
local commands = {
  {
      name      = "NextMap",
      arguments = {
          {"MapId", Admin.Command.ArgumentType.Int},
      },
      func      = function (player, role, MapId)
          if Admin.Game.NextMap(MapId) then
              Admin.SendConsoleMessageToAllPlayers(player .. " set next map id to " .. MapId)
          else
              Admin.SendConsoleMessageToPlayer(player, "Failed to set next map to " .. MapId)
          end
          
      end,
  },
  {
      name      = "NextMapName",
      arguments = {
          {"MapName", Admin.Command.ArgumentType.String},
      },
      func      = function (player, role, MapName)
          if Admin.Game.NextMapByFilename(MapName) then
              Admin.SendConsoleMessageToAllPlayers(player .. " set next map name to " .. MapId)
          else
              Admin.SendConsoleMessageToPlayer(player, "Failed to set next map to " .. MapName)
          end
          
      end,
  },
  {
      name      = "StartMap",
      arguments = {},
      func      = function (player, role)
          Admin.Game.StartMap()
          Admin.SendConsoleMessageToAllPlayers("Map started by " .. player)
      end,
  },
  {
      name      = "EndMap",
      arguments = {},
      func      = function (player, role)
          Admin.Game.EndMap()
          Admin.SendConsoleMessageToAllPlayers("Map ended by " .. player)
      end,
  },
}

function doSetupRoles(roles)
  for cmdIdx, command in pairs(commands) do
      Admin.Command.define(command.name, command.arguments, command.func)
  end
  
  for roleIdx, role in pairs(roles) do
      Admin.Roles.addLoginlessRole(role.name, role.canLua)
      for cmdIdx, cmdName in pairs(role.commands) do
          Admin.Roles.addAllowedCommand(role.name, cmdName)
      end
  end
end

local roles = {
    {
        name     = "admin",
        commands = {"NextMap", "NextMapName", "StartMap", "EndMap"},
        canLua   = true,
    },
    {
        name     = "mod",
        commands = {"NextMap", "NextMapName", "StartMap", "EndMap"},
        canLua   = false,
    },
  }
doSetupRoles(roles)

--------------------------------------------------------------------------------
Admin.Roles.addMember("admin", "siteadmin1")
Admin.Roles.addMember("admin", "siteadmin2")
Admin.Roles.addMember("mod", "siteuser1")
Admin.Roles.addMember("mod", "siteuser2")
