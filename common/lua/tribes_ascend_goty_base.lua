-- These settings are from https://github.com/Griffon26/tamods-server-gotylike
-- gotylike/serversettings.lua
----------------------------------------
Core.AllowUnmoddedClients = false

-- Limit all classes to two weapons
ServerSettings.DisabledEquipPoints.add("Light", Loadouts.EquipPoints.Tertiary)
ServerSettings.DisabledEquipPoints.add("Medium", Loadouts.EquipPoints.Tertiary)
ServerSettings.DisabledEquipPoints.add("Heavy", Loadouts.EquipPoints.Tertiary)
-- Time settings
ServerSettings.TimeLimit = 25
ServerSettings.RespawnTime = 5
ServerSettings.SniperRespawnDelay = 5
ServerSettings.EndMatchWaitTime = 45
ServerSettings.AmmoPickupLifespan = 60
ServerSettings.CTFFlagTimeout = 40
-- Team settings
ServerSettings.FriendlyFireMultiplier = 1
-- Vehicles
ServerSettings.VehiclesEarnedWithCredits = true
ServerSettings.GravCycleEjectionSeat = false
ServerSettings.BeowulfEjectionSeat = false
ServerSettings.ShrikeEjectionSeat = false
-- Inventory call-in
ServerSettings.EnableInventoryCallIn = true,
ServerSettings.InventoryStationsRestoreEnergy = true
ServerSettings.InventoryCallInBlocksPlayers = true
ServerSettings.InventoryCallInCost = 2000
ServerSettings.InventoryCallInBuildUpTime = 2.0
ServerSettings.InventoryCallInCooldownTime = 10.0
-- GOTY fixes
ServerSettings.UseGOTYShieldPack = true
ServerSettings.UseGOTYBXTCharging = true
ServerSettings.RageThrustPackDependsOnCapperSpeed = false

-- gotylike/utils.lua
----------------------------------------

-- Converts a list of mods in the form of {ModNameA = ValueA, ModNameB = ValueB}
-- Into the TAMods accepted form of { {ValueMods.ModNameA, ValueA}, {ValueMods.ModNameB, ValueB} }
function valueModsListDefConverter(valueModsList)
    local res = {}
    for modName, modVal in pairs(valueModsList) do
        table.insert(res, {ValueMods[modName], modVal})
    end
    return res
end

-- Helper for creating a custom class
function addClass(name, ootbBase, armorClass, weapons, beltItems, packs, skins)
    -- For GOTY, we only want to validate custom classes against equip points that existed in GOTY
    -- i.e. not tertiary weapons, which TAMods core uses to transport perk information
    local eqpPointsToValidate = {
        Loadouts.EquipPoints.Primary,
        Loadouts.EquipPoints.Secondary,
        Loadouts.EquipPoints.Pack,
        Loadouts.EquipPoints.Belt,
        Loadouts.EquipPoints.Skin,
    }

    ServerSettings.CustomClasses.new(name, ootbBase, armorClass, eqpPointsToValidate)
    for k, v in pairs(weapons) do
        ServerSettings.CustomClasses.addItem(name, v["class"] or ootbBase, v["name"] or v)
    end
    for k, v in pairs(beltItems) do
        ServerSettings.CustomClasses.addItem(name, v["class"] or ootbBase, v["name"] or v)
    end
    for k, v in pairs(packs) do
        ServerSettings.CustomClasses.addItem(name, v["class"] or ootbBase, v["name"] or v)
    end
    for k, v in pairs(skins) do
        ServerSettings.CustomClasses.addItem(name, v["class"] or ootbBase, v["name"] or v)
    end
end


-- gotylike/items.lua
----------------------------------------
-- Definitions here are for things which affect many weapons or cross-class weapons
-- Each class's weapons are defined in that class's individual definition
itemChangeDefs = {
    groups = {
        direct_hit_explosives = {
            -- Normal direct hit explosives (to change proj hitbox size)
            -- Light
            {class="Light", name="Light Spinfusor"},
            {class="Light", name="Dueling Spinfusor"},
            {class="Light", name="Stealth Spinfusor"},
            {class="Light", name="Light Twinfusor"},
            {class="Light", name="Blinksfusor"},
            {class="Light", name="Bolt Launcher"},
            -- Medium
            {class="Medium", name="Spinfusor"},
            {class="Medium", name="Twinfusor"},
            {class="Medium", name="Spare Spinfusor"},
            {class="Medium", name="Honorfusor"},
            {class="Medium", name="Thumper"},
            {class="Medium", name="Thumper D"},
            {class="Medium", name="Thumper DX"},
            -- Heavy
            {class="Heavy", name="Spinfusor MKD"},
            {class="Heavy", name="Spinfusor MK-X"},
            {class="Heavy", name="Heavy Spinfusor"},
            {class="Heavy", name="Devastator Spinfusor"},
            {class="Heavy", name="Heavy Twinfusor"},
            {class="Heavy", name="Heavy Bolt Launcher"},
            {class="Heavy", name="Spinfusor Disk"},
        },
        spinfusors = {
            -- Light
            {class="Light", name="Light Spinfusor"},
            {class="Light", name="Dueling Spinfusor"},
            {class="Light", name="Stealth Spinfusor"},
            {class="Light", name="Light Twinfusor"},
            {class="Light", name="Blinksfusor"},
            -- Medium
            {class="Medium", name="Spinfusor"},
            {class="Medium", name="Twinfusor"},
            {class="Medium", name="Spare Spinfusor"},
            {class="Medium", name="Honorfusor"},
            -- Heavy
            {class="Heavy", name="Spinfusor MKD"},
            {class="Heavy", name="Spinfusor MK-X"},
            {class="Heavy", name="Heavy Spinfusor"},
            {class="Heavy", name="Devastator Spinfusor"},
            {class="Heavy", name="Heavy Twinfusor"},
            {class="Heavy", name="Spinfusor Disk"},
        },
        chain = {
            -- For setting hitbox + damage falloff
            -- Falloff is between 4200 and 6000 Unreal Units, and down to 75% dmg
            -- Light
            {class="Light", name="Rhino SMG"},
            {class="Light", name="Arctic Rhino SMG"},
            {class="Light", name="Light Assault Rifle"},
            {class="Light", name="SN7 Pistol"},
            {class="Light", name="Arctic SN7 Pistol"},
            {class="Light", name="Falcon"},
            -- Medium
            {class="Medium", name="Assault Rifle"},
            {class="Medium", name="Gast Rifle"},
            {class="Medium", name="TCN4"},
            {class="Medium", name="TCN4 Rockwind"},
            {class="Medium", name="NJ4 SMG"},
            {class="Medium", name="Desert NJ4 SMG"},
            {class="Medium", name="NJ5 SMG"},
            -- Heavy
            {class="Heavy", name="Chain Gun"},
            {class="Heavy", name="Chain Cannon"},
            {class="Heavy", name="X1 LMG"},
        },
        hitscan_pistols = {
            {class="Light", name="Sparrow"},
            {class="Medium", name="Eagle"},
        },
        shotguns = {
            {class="Light", name="Shotgun"},
            {class="Light", name="Holdout Shotgun"},
            {class="Light", name="Accurized Shotgun"},
            {class="Medium", name="Sawed Off Shotgun"},
            {class="Heavy", name="Auto Shotgun"},
            {class="Heavy", name="The Hammer"},
        },
        explosive_weapon_dmg_banding = {
            -- All explosive weapons that use the common damage banding values
            -- of min damage of 50%, banding range between 50%-90% of damage radius
            -- Light
            {class="Light", name="Light Spinfusor"},
            {class="Light", name="Dueling Spinfusor"},
            {class="Light", name="Stealth Spinfusor"},
            {class="Light", name="Light Twinfusor"},
            {class="Light", name="Blinksfusor"},
            {class="Light", name="Bolt Launcher"},
            {class="Light", name="Light Grenade Launcher"},
            {class="Light", name="Jackal"},
            -- Medium
            {class="Medium", name="Spinfusor"},
            {class="Medium", name="Twinfusor"},
            {class="Medium", name="Spare Spinfusor"},
            {class="Medium", name="Honorfusor"},
            {class="Medium", name="Thumper"},
            {class="Medium", name="Thumper D"},
            {class="Medium", name="Thumper DX"},
            {class="Medium", name="Arx Buster"},
            {class="Medium", name="Dust Devil"},
            {class="Medium", name="Grenade Launcher"},
            {class="Medium", name="Plasma Gun"},
            {class="Medium", name="Cluster Grenade"},
            -- Heavy
            {class="Heavy", name="Fusion Mortar"},
            {class="Heavy", name="Fusion Mortar Deluxe"},
            {class="Heavy", name="MIRV Launcher"},
            {class="Heavy", name="Spinfusor MKD"},
            {class="Heavy", name="Spinfusor MK-X"},
            {class="Heavy", name="Spinfusor Disk"},
            {class="Heavy", name="Heavy Spinfusor"},
            {class="Heavy", name="Devastator Spinfusor"},
            {class="Heavy", name="Heavy Twinfusor"},
            {class="Heavy", name="Heavy Bolt Launcher"},
            {class="Heavy", name="Saber Launcher"},
            {class="Heavy", name="Titan Launcher"},
            {class="Heavy", name="Plasma Cannon"},
        },
        grenade_dmg_banding = {
            -- All explosive grenades that use the common damage banding values
            -- of min damage of 30%, banding range between 50%-90% of damage radius
            -- Light
            {class="Light", name="Impact Nitron"},
            {class="Light", name="Explosive Nitron"},
            {class="Light", name="Compact Nitron"},
            {class="Light", name="Sticky Grenades"},
            {class="Light", name="Sticky Grenade XL"},
            {class="Light", name="Sticky Grenade XL"},
            {class="Light", name="Chaff Grenade"},
            {class="Light", name="T5 Grenade"},
            {class="Medium", name="Frag Grenade XL"},
            {class="Medium", name="Short-Fuse Frag Grenade"},
            {class="Medium", name="AP Grenade"},
            {class="Medium", name="Proximity Grenade"},
            {class="Medium", name="EMP Grenade"},
            {class="Medium", name="EMP XL Grenade"},
            {class="Medium", name="Blackout Grenade"},
            {class="Medium", name="TCNG"},
            {class="Medium", name="TCNG Quickfuse"},
            {class="Heavy", name="Heavy AP Grenade"},
            {class="Heavy", name="Heavy AP-XL"},
            {class="Heavy", name="Heavy AP-XL"},
            {class="Heavy", name="Frag Grenade"},
            {class="Heavy", name="Light Sticky Grenade"},
        },
    },
    mods = {
        ---------------------
        -- GROUPS
        ---------------------
        {
            group="direct_hit_explosives",
            changes={
                -- Same as GOTY, smaller than OOTB
                CollisionSize = 10,
            }
        },
        {
            group="explosive_weapon_dmg_banding",
            changes={
                -- GOTY damage banding
                MinDamageProportion = 0.5,
                MaxDamageRangeProportion = 0.5,
                MinDamageRangeProportion = 0.9,
                SelfImpactMomentumMultiplier = 1.2,
                SelfImpactExtraZMomentum = 90000,
                DamageAgainstShrikeMultiplier = 3,
                DamageAgainstGravCycleMultiplier = 1.2,
                DamageAgainstBeowulfMultiplier = 1.2,
            }
        },
        {
            group="grenade_dmg_banding",
            changes={
                -- GOTY damage banding
                MinDamageProportion = 0.3,
                MaxDamageRangeProportion = 0.5,
                MinDamageRangeProportion = 0.9,
                CollisionSize = 42,
                DamageAgainstShrikeMultiplier = 0.25,
                DamageAgainstGravCycleMultiplier = 1.2,
                DamageAgainstBeowulfMultiplier = 1.2,
                SelfImpactExtraZMomentum = 90000,
            }
        },
        {
            group="chain",
            changes={
                Accuracy = 0.98,
                AccuracyLossOnShot = 0,
                AccuracyLossMax = 0.11,
                AccuracyCorrectionRate = 0.19,
                CollisionSize = 50,
                ProjectileLifespan = 1.0,
                -- GOTY damage falloff
                MinDamageProportion = 0.75,
                MaxDamageRangeProportion = 0.75,
                MinDamageRangeProportion = 1,
                DamageAgainstShrikeMultiplier = 0.65,
                DamageAgainstGravCycleMultiplier = 0,
                DamageAgainstBeowulfMultiplier = 0,
            }
        },
        {
            group="shotguns",
            changes={
                -- GOTY falloff
                MinDamageProportion = 0.3,
                MaxDamageRangeProportion = 0.5,
                MinDamageRangeProportion = 0.9,
                DamageAgainstShrikeMultiplier = 0.65,
                DamageAgainstGravCycleMultiplier = 0,
                DamageAgainstBeowulfMultiplier = 0,
            }
        },
        {
            group="hitscan_pistols",
            changes={
                HitscanRange=10000,
                MinDamageProportion = 0.4,
                MaxDamageRangeProportion = 0.2,
                MinDamageRangeProportion = 0.4,
                DamageAgainstShrikeMultiplier = 0.65,
                DamageAgainstGravCycleMultiplier = 0,
                DamageAgainstBeowulfMultiplier = 0,
            }
        },
        ---------------------
        -- CROSS-CLASS
        ---------------------
        {
            class="Light", -- Will apply across classes
            name="Melee",
            changes={
                Damage = 900,
            },
        },


        ---------------------
        -- PERKS
        ---------------------
        {
            class="Light", -- Will apply across classes
            name="Bounty Hunter",
            valueMods={
                -- This doesn't do anything because credits don't exist...
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Close Combat",
            valueMods={
                MeleeDamageReduction = 0.6,
                BackstabMeleeBuff = 1,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Determination",
            valueMods={
                Determination = true,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Egocentric",
            valueMods={
                SelfDamageReduction = 0.35,
                IgnoreGrenadeEffectsOnSelf = true,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Lightweight",
            valueMods={
                MassBuff = -0.3,
                RegenTimeBuff = -2.0
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Looter",
            valueMods={
                AmmoPickupBuff = 1.0,
                BeltPickupBuff = 1,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Mechanic",
            valueMods={
                RepairToolDamagesEnemyObjectives = true,
                RepairRateBuff = 0.2,
                VehiclePassengerDamageReductionBuff = 0.25,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Pilot",
            valueMods={
                VehicleHealthBuff = 0.2,
                EjectionSeat = true,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Potential Energy",
            valueMods={
                PotentialEnergy = true,
                PotentialEnergyDamageTransferBuff = 0.06,
                PotentialEnergyOnFallDamage = true,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Quick Draw",
            valueMods={
                QuickDraw = 0.5,
                QuickDrawBelt = 0.2,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Rage",
            valueMods={
                Rage = true,
                RageTime = 15,
                RageEnergyRegen = 0.2,
                RageMassChange = -0.2,
                RageHealthRestoration = 0.5,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Reach",
            valueMods={
                Reach = true,
                ReachTier = 3,
                ReachOnPickups = true,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Safe Fall",
            valueMods={
                FallDamageReduction = 1.0,
                RunoverDamageReduction = 1.0,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Safety Third",
            valueMods={
                ExtraBeltAmmo = 1,
                BeltDamageRadiusBuff = 0.1,
                ExtraMines = 1,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Sonic Punch",
            valueMods={
                SonicPunch = true,
                SonicPunchRange = 315,
                SonicPunchKnockback = 750,
                SonicPunchFlagDrop = true,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Stealthy",
            valueMods={
                Stealthy = 0.9,
                TurretTargetAcquisitionBuff = 0.3,
            }
        },
        {
            class="Light", -- Will apply across classes
            -- aka Ultra Capacitor I
            name="Super Capacitor",
            valueMods={
                EnergyBuff = 10,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Super Heavy",
            valueMods={
                MassBuff = 0.8,
                SuperHeavy = true,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Survivalist",
            valueMods={
                SurvivalistHealth = 0.2,
                SurvivalistEnergy = 0.4,
            }
        },
        {
            class="Light", -- Will apply across classes
            -- aka Ultra Capacitor II
            name="Ultra Capacitor",
            valueMods={
                EnergyBuff = 10,
            }
        },
        {
            class="Light", -- Will apply across classes
            name="Wheel Deal",
            valueMods={
                VehicleCostReduction = 0.3,
                VehicleEnergyBuff = 0.25,
            }
        },
    },
}

for modIdx, modDef in pairs(itemChangeDefs.mods) do
    -- Find item/s to apply on
    local itemsToApplyTo = {}
    if modDef.group ~= nil then
        for gpIdx, item in pairs(itemChangeDefs.groups[modDef.group]) do
            table.insert(itemsToApplyTo, item)
        end
    else
        table.insert(itemsToApplyTo, {class=modDef.class, name=modDef.name})
    end

    -- Apply each property
    if modDef.changes ~= nil then
        for changeProp, changeVal in pairs(modDef.changes) do
            for itemIdx, item in pairs(itemsToApplyTo) do
                Items.setProperty(item.class, item.name, Items.Properties[changeProp], changeVal)
            end
        end
    end

    -- Apply each valuemod
    if modDef.valueMods ~= nil then
        for itemIdx, item in pairs(itemsToApplyTo) do
            Items.setValueMods(item.class, item.name, utils:valueModsListDefConverter(modDef.valueMods))
        end
    end

end

-- gotylike/definitions/Pathfinder.lua
----------------------------------------
pathfinderClassDef =  {
    ootbClass="Light",
    armorClass="Pathfinder",
    weapons={
        "Light Spinfusor",
        "Bolt Launcher",
        "Blinksfusor",
        "Light Twinfusor",
        "Dueling Spinfusor",
        -- "Light Grenade Launcher",
        "Light Assault Rifle",
        "Shotgun",
        "Holdout Shotgun",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "Impact Nitron",
        "Explosive Nitron",
        "Compact Nitron",
    },
    packs={
        "Thrust Pack",
        -- The Energy pack is the SEN one now
        -- But in GOTY the two were identical
        "Light Energy Pack",
        -- Light Utility pack is being converted
        -- into a 'Lightweight pack'
        "Light Utility Pack",
    },
    skins={
        "Pathfinder",
        "Freerunner",
    },
    properties={
        HealthPool = 800,
        RegenTime = 20,
        Mass = 100,
        RegenRate = 0.1,
        EnergyPool = 100,
        EnergyRechargeRate = 14,
        GroundSpeed = 500,
        AirControlMaxMultiplier = 3.7,
        AirControlMinMultiplier = 1.4,
        VehicleSpeedInheritance = 1,
    },
    armorValueMods={
        -- Pathfinder Armor Upgrades
        RegenTimeBuff = 0.25,
        EnergyBuff = 10,
        HealthRegenRateBuff = 0.25,
        HealthBuff = 100,
        -- MassBuff = -0.1,
    }
}
pathfinderItemsDef = {
    {
        name="Light Spinfusor",
        changes={
            Damage = 550,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 28,
            ReloadTime = 1.24,
        },
    },
    {
        name="Dueling Spinfusor",
        changes={
            Damage = 550,
            DirectHitMultiplier = 1.6,
            SpareAmmo = 28,
            ReloadTime = 1.24,
            ExplosiveRadius = 340,
        },
    },
    {
        name="Blinksfusor",
        changes={
            Damage = 550,
            DirectHitMultiplier = 1.6,
            SpareAmmo = 28,
            ReloadTime = 1.24,
        },
    },
    {
        name="Light Twinfusor",
        changes={
            Damage = 380,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 36,
            ImpactMomentum = 85000,
            SelfImpactMomentumMultiplier = 0.5,
            SelfImpactExtraZMomentum = 45000,
            ReloadTime = 1.4,
        },
    },
    {
        name="Bolt Launcher",
        changes={
            Damage = 650,
            DirectHitMultiplier = 1.35,
            SpareAmmo = 28,
        },
    },
    {
        name="Light Assault Rifle",
        changes={
            Damage = 80,
            ClipAmmo = 24,
            SpareAmmo = 204,
            ReloadTime = 1.53,
            FireInterval = 0.1,
        },
    },
    {
        name="Shotgun",
        changes={
            Damage = 80,
            ShotgunShotCount = 8,
            ClipAmmo = 6,
            SpareAmmo = 50,
            HitscanRange = 3000,
            Accuracy = 0.85,
            AccuracyLossMax = 0.3,
            AccuracyLossOnShot = 0.0,
            AccuracyCorrectionRate = 0.18,
            ShotgunUseGOTYSpread = true,
        },
    },
    {
        name="Holdout Shotgun",
        changes={
            Damage = 85,
            ShotgunShotCount = 8,
            ClipAmmo = 5,
            SpareAmmo = 46,
            HitscanRange = 3000,
            Accuracy = 0.85,
            AccuracyLossMax = 0.3,
            AccuracyLossOnShot = 0.0,
            AccuracyCorrectionRate = 0.18,
            ShotgunUseGOTYSpread = true,
        },
    },
    {
        name="Impact Nitron",
        changes={
            Damage=300,
            ExplosiveRadius=506,
            DirectHitMultiplier=1,
            SpareAmmo=3,
        },
    },
    {
        name="Explosive Nitron",
        changes={
            Damage=650,
            ExplosiveRadius=396,
            DirectHitMultiplier=1,
            SpareAmmo=3,
        },
    },
    {
        name="Compact Nitron",
        changes={
            Damage=300,
            ExplosiveRadius=440,
            DirectHitMultiplier=1,
            SpareAmmo=4,
        },
    },
    {
        name="Light Energy Pack",
        valueMods={
            EnergyRegenRateBuff=0.18
        },
    },
    {
        -- Converted into a 'lightweight pack'
        name="Light Utility Pack",
        valueMods={
            EnergyBuff=25,
            MassBuff=-0.3
        },
    },
    {
        -- Converted into a 'lightweight pack'
        name="Shocklance",
        changes={
            Damage = 700,
            HitscanRange = 500,
            ShotEnergyCost = 10,
        },
    },
}

-- gotylike/definitions/Infiltrator.lua
----------------------------------------
infiltratorClassDef = {
    ootbClass="Light",
    armorClass="Infiltrator",
    weapons={
        "Stealth Spinfusor",
        "Jackal",
        "Rhino SMG",
        "Arctic Rhino SMG",
        "SN7 Pistol",
        "Arctic SN7 Pistol",
        "Throwing Knives",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "Sticky Grenades",
        "Sticky Grenades XL",
        "Prism Mines",
        "Chaff Grenades",
    },
    packs={
        "Stealth Pack",
    },
    skins={
        "Infiltrator",
        "Mercenary",
        "Assassin",
    },
    properties={
        HealthPool = 800,
        RegenTime = 20,
        Mass = 100,
        RegenRate = 0.1,
        VehicleSpeedInheritance = 1,
    },
    armorValueMods={
        -- Infiltrator Armor Upgrades
        RegenTimeBuff = 0.25,
        EnergyBuff = 10,
        HealthBuff = 200,
        WalkSpeedBuff = 0.1,
    }
}
infiltratorItemDefs = {
    {
        name="Stealth Spinfusor",
        changes={
            Damage = 500,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 28,
        },
    },
    {
        name="Jackal",
        changes={
            Damage = 200,
            ExplosiveRadius = 360,
            StuckDamageMultiplier = 2,
            StuckMomentumMultiplier = 2,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 39,
            FireInterval = 0.35,
        },
    },
    {
        name="Rhino SMG",
        changes={
            Damage = 70,
            ClipAmmo = 30,
            SpareAmmo = 260,
            ReloadTime = 1.53,
            FireInterval = 0.1,
        },
    },
    {
        name="Arctic Rhino SMG",
        changes={
            Damage = 80,
            ClipAmmo = 30,
            SpareAmmo = 260,
            ReloadTime = 1.53,
            FireInterval = 0.11,
        },
    },
    {
        name="SN7 Pistol",
        changes={
            Damage = 170,
            ClipAmmo = 16,
            SpareAmmo = 84,
            ReloadTime = 1.26,
            FireInterval = 0.2,
            HoldToFire = false,
        },
    },
    {
        name="Arctic SN7 Pistol",
        changes={
            Damage = 180,
            ClipAmmo = 14,
            SpareAmmo = 80,
            ReloadTime = 1.26,
            FireInterval = 0.2,
            HoldToFire = false,
        },
    },
    {
        name="Throwing Knives",
        changes={
            Damage = 100,
            DirectHitMultiplier = 3.75,
            ExplosiveRadius = 120,
            ProjectileSpeed = 15000,
            ProjectileLifespan = 1.0,
            ClipAmmo = 6,
            SpareAmmo = 35,
            ReloadTime = 1.26,
            FireInterval = 0.5,
            MinDamageProportion = 1, -- No falloff
            CollisionSize = 50,
        },
    },
    {
        name="Sticky Grenade",
        changes={
            Damage = 1000,
            ExplosiveRadius = 555,
            StuckDamageMultiplier = 1,
            StuckMomentumMultiplier = 1,
            ProjectileSpeed = 1200,
            SpareAmmo = 4,
        }
    },
    {
        name="Sticky Grenade XL",
        changes={
            Damage = 800,
            ExplosiveRadius = 660,
            StuckDamageMultiplier = 1,
            StuckMomentumMultiplier = 1,
            ProjectileSpeed = 1200,
            SpareAmmo = 4,
        }
    },
    {
        name="Prism Mines",
        changes={
            Damage = 800,
            ExplosiveRadius = 583,
            PrismMineTripDistance = 512,
            MineDeployTime=2,
            MineMaxAllowed=3,
            MineCollisionCylinderRadius=300,
            MineCollisionCylinderHeight=100,
            SpareAmmo=3,
        }
    },
    {
        name="Stealth Pack",
        changes={
            PackSustainedEnergyCost = 5,
        }
    },
}

-- gotylike/definitions/Sentinel.lua
----------------------------------------
sentinelClassDef = {
    ootbClass="Light",
    armorClass="Sentinel",
    weapons={
        "BXT1",
        "BXT1A",
        "Phase Rifle",
        "SAP20",
        {class="Medium", name="Nova Blaster"},
        {class="Heavy", name="Nova Blaster MX"},
        "Falcon",
        "Accurized Shotgun",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "T5 Grenades",
        "Claymore Mines",
        "Motion Mines",
    },
    packs={
        "Light Energy Pack",
    },
    skins={
        "Sentinel",
        "Specter",
    },
    properties={
        HealthPool = 800,
        RegenTime = 20,
        Mass = 100,
        RegenRate = 0.1,
        EnergyPool = 90,
        VehicleSpeedInheritance = 1,
    },
    armorValueMods={
        -- Sentinel Armor Upgrades
        RegenTimeBuff = 0.25,
        WalkSpeedBuff = 0.1,
        HealthRegenRateBuff = 0.25,
        HealthBuff = 100,
        EnergyBuff = 10,
        ExtraBeltAmmo = 1,
        ExtraMines = 1
    }
}
sentinelItemDefs = {
    {
        name="BXT1",
        changes={
            Damage = 10, -- Uncharged damage
            BXTChargeMaxDamage = 500,
            BXTChargeTime = 2.5,
            BXTChargeMultCoefficient = 16,
            BXTChargeDivCoefficient = 100,
            ReloadTime = 1.4,
            FireInterval = 1.0,
            ClipAmmo = 5,
            SpareAmmo = 32,
            HitscanRange = 100000,
            MinDamageProportion = 0.45,
            MaxDamageRangeProportion = 0.12,
            MinDamageRangeProportion = 0.24,
            DamageAgainstShrikeMultiplier = 0.1,
        },
    },
    {
        name="BXT1A",
        changes={
            Damage = 10, -- Uncharged damage
            BXTChargeMaxDamage = 500,
            BXTChargeTime = 2.8,
            BXTChargeMultCoefficient = 16,
            BXTChargeDivCoefficient = 100,
            ReloadTime = 1.4,
            FireInterval = 1.0,
            ClipAmmo = 6,
            SpareAmmo = 34,
            HitscanRange = 100000,
            MinDamageProportion = 0.45,
            MaxDamageRangeProportion = 0.12,
            MinDamageRangeProportion = 0.24,
            DamageAgainstShrikeMultiplier = 0.1,
        },
    },
    {
        name="Phase Rifle",
        changes={
            Damage = 60, -- Damage with no energy
            PhaseDamagePerEnergy = 5.0,
            PhaseMaxConsumedEnergy = 90.0,
            ReloadTime = 1.4,
            FireInterval = 1.0,
            ClipAmmo = 5,
            SpareAmmo = 32,
            HitscanRange = 100000,
            MinDamageProportion = 0.45,
            MaxDamageRangeProportion = 0.12,
            MinDamageRangeProportion = 0.24,
            DamageAgainstShrikeMultiplier = 0.1,
        },
        valueMods={}
    },
    {
        name="SAP20",
        changes={
            Damage = 100, -- Damage with no energy
            PhaseDamagePerEnergy = 5.0,
            PhaseMaxConsumedEnergy = 95.0,
            ReloadTime = 1.4,
            FireInterval = 1.0,
            ClipAmmo = 3,
            SpareAmmo = 32,
            HitscanRange = 100000,
            MinDamageProportion = 0.45,
            MaxDamageRangeProportion = 0.12,
            MinDamageRangeProportion = 0.24,
            DamageAgainstShrikeMultiplier = 0.1,
        },
        valueMods={}
    },
    {
        name="Falcon",
        changes={
            Damage = 65,
            ProjectileInheritance = 0,
            ClipAmmo = 24,
            ReloadTime = 1.53,
            FireInterval = 0.1,
        },
    },
    {
        class="Medium",
        name="Nova Blaster",
        changes={
            Damage = 350,
            ProjectileSpeed = 8000,
            ProjectileLifespan = 1,
            ClipAmmo = 16,
            SpareAmmo = 96,
            ReloadTime = 1.4,
            FireInterval = 0.35,
            MinDamageProportion = 1,
            MaxDamageRangeProportion = 0.2,
            MinDamageRangeProportion = 0.4,
            HoldToFire = false,
        },
    },
    {
        class="Heavy",
        name="Nova Blaster MX",
        changes={
            Damage = 250,
            ProjectileSpeed = 8000,
            ProjectileLifespan = 1,
            ClipAmmo = 20,
            SpareAmmo = 128,
            ReloadTime = 1.4,
            FireInterval = 0.25,
            MinDamageProportion = 1,
            MaxDamageRangeProportion = 0.2,
            MinDamageRangeProportion = 0.4,
            HoldToFire = false,
        },
    },
    {
        name="Accurized Shotgun",
        changes={
            Damage = 70,
            ShotgunShotCount = 8,
            ClipAmmo = 6,
            SpareAmmo = 50,
            HitscanRange = 3000,
            Accuracy = 0.86,
            AccuracyLossMax = 0.3,
            AccuracyLossOnShot = 0.0,
            AccuracyCorrectionRate = 0.18,
            ShotgunUseGOTYSpread = true,
        },
    },
    {
        name="Claymore Mines",
        changes={
            Damage=700,
            DamageAgainstArmorMultiplier=0.50,
            DamageAgainstGeneratorMultiplier=1.0,
            DamageAgainstBeowulfMultiplier=0.50,
            DamageAgainstGravCycleMultiplier=0.50,
            DamageAgainstBaseTurretMultiplier=2.50,
            DamageAgainstBaseSensorMultiplier=2.50,
            DamageAgainstShrikeMultiplier=2.50,
        },
    },
    {
        name="T5 Grenades",
        changes={
            Damage = 1100,
            ExplosiveRadius = 682,
            SpareAmmo = 2,
        },
    },
}

-- gotylike/definitions/Soldier.lua
----------------------------------------
soldierClassDef = {
    ootbClass="Medium",
    armorClass="Soldier",
    weapons={
        "Spinfusor",
        "Twinfusor",
        "Honorfusor",
        "Assault Rifle",
        "Gast Rifle",
        "Spare Spinfusor",
        "Thumper D",
        "Thumper DX",
        "Eagle",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "Frag Grenades XL",
        "Short-Fuse Frag Grenades",
        "AP Grenades",
        "Proximity Grenades",
    },
    packs={
        "Energy Pack",
        "Utility Pack",
    },
    skins={
        "Soldier",
        "Synthrall",
    },
    properties={
        HealthPool = 1200,
        RegenTime = 20,
        RegenRate = 0.1,
        Mass = 100,
        VehicleSpeedInheritance = 1,
        CollisionCylinderRadius = 24,
        CollisionCylinderHeight = 46,
    },
    armorValueMods={
        -- Soldier Armor Upgrades
        RegenTimeBuff = 0.25,
        HealthBuff = 100,
        HealthRegenRateBuff = 0.25,
        EnergyBuff = 5,
    }
}
soldierItemDefs = {
    {
        name="Spinfusor",
        changes={
            Damage = 650,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 28,
            ReloadTime = 1.5,
        },
    },
    {
        name="Honorfusor",
        changes={
            Damage = 650,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 28,
            ReloadTime = 1.5,
        },
    },
    {
        name="Twinfusor",
        changes={
            Damage = 410,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 36,
            ImpactMomentum = 85000,
            SelfImpactMomentumMultiplier = 0.5,
            SelfImpactExtraZMomentum = 45000,
            ReloadTime = 1.6,
        },
    },
    {
        name="Assault Rifle",
        changes={
            Damage = 80,
            ClipAmmo = 28,
            ReloadTime = 1.53,
            FireInterval = 0.11,
            SpareAmmo = 240,
        },
    },
    {
        name="Gast Rifle",
        changes={
            ClipAmmo = 24,
            SpareAmmo = 200,
            ReloadTime = 1.53,
        },
    },
    {
        name="Thumper D",
        changes={
            Damage = 550,
            ExplosiveRadius = 370,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 20,
            SelfImpactExtraZMomentum = 70000,
        },
    },
    {
        name="Thumper DX",
        changes={
            Damage = 600,
            ExplosiveRadius = 350,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 20,
            SelfImpactExtraZMomentum = 70000,
        },
    },
    {
        name="Spare Spinfusor",
        changes={
            Damage = 600,
            DirectHitMultiplier = 1.1,
            SpareAmmo = 28,
            ProjectileInheritance = 0.5,
            ReloadTime = 1.5,
        },
    },
    {
        name="Eagle",
        changes={
            HoldToFire = false,
            Damage = 100,
            ClipAmmo = 20,
            SpareAmmo = 132,
            ReloadTime = 1.26,
            FireInterval = 0.16,
            -- Accuracy = 0.98,
            -- AccuracyLossOnShot = 0.45,
            -- AccuracyLossMax = 0.1,
            -- AccuracyCorrectionRate = 0.38,
            Accuracy = 0.9875,
            AccuracyLossOnShot = 0.45,
            AccuracyLossMax = 0.1,
            AccuracyCorrectionRate = 0.38,

            -- AccuracyCorrectionRate = 0.39,
        },
    },
    {
        name="Frag Grenade XL",
        changes={
            Damage = 1000,
            ExplosiveRadius = 682,
            SpareAmmo = 2,
        },
    },
    {
        name="Short-Fuse Frag Grenades",
        changes={
            Damage = 720,
            ExplosiveRadius = 550,
            SpareAmmo = 2,
        },
    },
    {
        name="AP Grenades",
        changes={
            Damage = 1200,
            ExplosiveRadius = 600,
            SpareAmmo = 2,
        },
    },
    {
        name="Proximity Grenades",
        changes={
            Damage = 620,
            ExplosiveRadius = 528,
            SpareAmmo = 2,
        },
    },
    {
        name="Energy Pack",
        valueMods={
            EnergyBuff = 35,
        },
    },
    {
        name="Utility Pack",
        valueMods={
            EnergyBuff = 20,
            ExtraBeltAmmo = 1,
            HealthBuff = 100,
            WalkSpeedBuff = 0.1,
        },
    },
}

-- gotylike/definitions/Raider.lua
----------------------------------------
raiderClassDef = {
    ootbClass="Medium",
    armorClass="Raider",
    weapons={
        "Arx Buster",
        "Dust Devil",
        "Grenade Launcher",
        "Plasma Gun",
        "NJ4 SMG",
        "Desert NJ4 SMG",
        "NJ5 SMG",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "EMP Grenade",
        "EMP XL Grenade",
        "Blackout Grenade",
        "Cluster Grenade",
    },
    packs={
        "Shield Pack",
        "Jammer Pack",
    },
    skins={
        "Raider",
        "Mercenary",
        "Griever",
    },
    properties={
        HealthPool = 1200,
        RegenTime = 20,
        Mass = 100,
        RegenRate = 0.1,
        VehicleSpeedInheritance = 1,
        CollisionCylinderRadius = 24,
        CollisionCylinderHeight = 46,
    },
    armorValueMods={
        -- Raider Armor Upgrades
        RegenTimeBuff = 0.25,
        HealthBuff = 100,
        HealthRegenRateBuff = 0.25,
        EnergyBuff = 10,
    }
}
raiderItemDefs = {
    {
        name="Arx Buster",
        changes={
            Damage = 600,
            StuckDamageMultiplier = 1,
            StuckMomentumMultiplier = 1,
            ExplosiveRadius = 360,
            SpareAmmo = 39,
        },
    },
    {
        name="Dust Devil",
        changes={
            Damage = 500,
            StuckDamageMultiplier = 1,
            StuckMomentumMultiplier = 1,
            ExplosiveRadius = 410,
            SpareAmmo = 39,
        },
    },
    {
        name="Grenade Launcher",
        changes={
            Damage = 550,
            ExplosiveRadius = 500,
            ClipAmmo = 5,
            SpareAmmo = 46,
        },
    },
    {
        name="Plasma Gun",
        changes={
            Damage = 400,
            DirectHitMultiplier = 1.25,
            ExplosiveRadius = 270,
            ProjectileInheritance = 0.5,
            ProjectileSpeed = 3620,
            ProjectileMaxSpeed = 8000,
            ProjectileLifespan = 3,
            SelfImpactExtraZMomentum = 25000,
            ClipAmmo = 6,
            SpareAmmo = 50,
            ReloadTime = 1.8,
            FireInterval = 0.47,
            DamageAgainstShrikeMultiplier = 0.1,
        },
    },
    {
        name="NJ4 SMG",
        changes={
            Damage = 75,
            ProjectileInheritance = 0,
            ClipAmmo = 28,
            SpareAmmo = 240,
            ReloadTime = 1.53,
            FireInterval = 0.11,
        },
    },
    {
        name="Desert NJ4 SMG",
        changes={
            Damage = 70,
            ProjectileInheritance = 0,
            ClipAmmo = 28,
            SpareAmmo = 240,
            ReloadTime = 1.53,
            FireInterval = 0.1,
        },
    },
    {
        name="NJ5 SMG",
        changes={
            Damage = 125,
            ClipAmmo = 24,
            SpareAmmo = 216,
            ReloadTime = 1.53,
            FireInterval = 0.2,
            Accuracy = 0.99,
        },
    },
    {
        name="EMP Grenade",
        changes={
            Damage = 600,
            ExplosiveRadius = 682,
            EnergyDrain = 192,
            SpareAmmo = 2,
        }
    },
    {
        name="EMP XL Grenade",
        changes={
            Damage = 500,
            ExplosiveRadius = 858,
            EnergyDrain = 192,
            SpareAmmo = 2,
        }
    },
    {
        name="Blackout Grenade",
        changes={
            Damage = 50,
            SelfImpactExtraZMomentum = 50000,
        }
    },
    {
        name="Shield Pack",
        changes={
            ShieldPackEnergyCostPerDamagePoint = 0.16,
            PackSustainedEnergyCost = 1.5,
        },
        valueMods={
            ShieldPackBuff = 0.01,
        },
    },
    {
        name="Jammer Pack",
        changes={
            PackSustainedEnergyCost = 1.75,
            JammerPackRange = 1300,
        }
    },
}

-- gotylike/definitions/Technician.lua
----------------------------------------
technicianClassDef = {
    ootbClass="Medium",
    armorClass="Technician",
    weapons={
        "Thumper",
        "TCN4",
        "TCN4 Rockwind",
        "Flak Cannon",
        "Improved Repair Tool",
        "Sawed Off Shotgun",
        {class="Light", name="Shocklance"},
        {class="Light", name="Sparrow"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "TCNG",
        "TCNG Quickfuse",
        "Motion Sensor",
    },
    packs={
        "Light Turret",
        "EXR Turret",
    },
    skins={
        "Technician",
        "Specialist",
    },
    properties={
        HealthPool = 1200,
        RegenTime = 20,
        Mass = 100,
        RegenRate = 0.1,
        VehicleSpeedInheritance = 1,
        CollisionCylinderRadius = 24,
        CollisionCylinderHeight = 46,
    },
    armorValueMods={
        -- Technician Armor Upgrades
        RegenTimeBuff = 0.25,
        HealthBuff = 100,
        HealthRegenRateBuff = 0.25,
        EnergyBuff = 10,
        ExtraDeployables = 1,
    },
}
technicianItemDefs = {
    {
        name="Thumper",
        changes={
            Damage = 650,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 35,
        },
    },
    {
        name="TCN4",
        changes={
            Damage = 80,
            ClipAmmo = 32,
            SpareAmmo = 336,
            ReloadTime = 1.53,
        },
    },
    {
        name="TCN4 Rockwind",
        changes={
            Damage = 105,
            ClipAmmo = 24,
            SpareAmmo = 240,
            ReloadTime = 1.53,
            FireInterval = 0.15,
        },
    },
    {
        name="Sawed Off Shotgun",
        changes={
            Damage = 80,
            ShotgunShotCount = 8,
            ClipAmmo = 2,
            SpareAmmo = 50,
            HitscanRange = 3000,
            ReloadTime = 1.28,
            Accuracy = 0.85,
            AccuracyLossMax = 0.3,
            AccuracyLossOnShot = 0.0,
            AccuracyCorrectionRate = 0.18,
            ShotgunUseGOTYSpread = true,
        },
    },
    {
        class="Light",
        name="Sparrow",
        changes={
            HoldToFire = false,
            Damage = 90,
            ClipAmmo = 28,
            SpareAmmo = 188,
            ReloadTime = 1.26,
            FireInterval = 0.16,
            -- Accuracy = 0.98,
            AccuracyLossOnShot = 0.45,
            AccuracyLossMax = 0.1,
            AccuracyCorrectionRate = 0.38,
        },
    },
    {
        name="TCNG",
        changes={
            Damage = 900,
            ExplosiveRadius = 572,
            SpareAmmo = 2,
        },
    },
    {
        name="TCNG Quickfuse",
        changes={
            Damage = 700,
            ExplosiveRadius = 528,
            SpareAmmo = 2,
            FuseTimer = 1.2,
        },
    },
    {
        name="Motion Sensor",
        changes={
            Damage = 10,
            EnergyDrain = 100,
            ImpactMomentum = 1000,
            ExplosiveRadius = 572,
            SpareAmmo = 2,
            MineCollisionCylinderRadius = 300,
            MineCollisionCylinderHeight = 200,
        },
    },
}

-- gotylike/definitions/Juggernaut.lua
----------------------------------------
juggernautClassDef = {
    ootbClass="Heavy",
    armorClass="Juggernaught",
    weapons={
        "Fusion Mortar",
        "Fusion Mortar Deluxe",
        "MIRV Launcher",
        "Spinfusor MKD",
        "Spinfusor MK-X",
        "Heavy Twinfusor",
        "X1 LMG",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "Heavy AP Grenade",
        "Heavy AP-XL",
        "Spinfusor Disk",
    },
    packs={
        "Regen Pack",
    },
    skins={
        "Juggernaut",
        "The Forlorn",
    },
    properties={
        HealthPool = 2400,
        RegenTime = 20,
        RegenRate = 0.1,
        EnergyPool = 80,
        EnergyRechargeRate = 9,
        GroundSpeed = 360,
        Mass = 130,
        AirControlMaxMultiplier = 3.7,
        AirControlMinMultiplier = 0.4,
        VehicleSpeedInheritance = 0.75,
    },
    armorValueMods={
        -- Juggernaught Armor Upgrades
        HealthBuff = 200,
        RegenTimeBuff = 0.25,
        EnergyBuff = 10,
        HealthRegenRateBuff = 0.25,
    }
}
juggernautItemDefs = {
    {
        name="Fusion Mortar",
        changes={
            Damage = 1300,
            DirectHitMultiplier = 1,
            ExplosiveRadius = 700,
            ProjectileSpeed = 3500,
            ProjectileMaxSpeed = 7000,
            ProjectileTerminalVelocity = 7000,
            SpareAmmo = 25,
        },
    },
    {
        name="Fusion Mortar Deluxe",
        changes={
            Damage = 1400,
            DirectHitMultiplier = 1,
            ExplosiveRadius = 650,
            ProjectileSpeed = 4000,
            ProjectileMaxSpeed = 8000,
            ProjectileTerminalVelocity = 8000,
            SpareAmmo = 25,
        },
    },
    {
        name="Spinfusor MKD",
        changes={
            Damage = 600,
            ExplosiveRadius = 390,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 28,
            ReloadTime = 1.5,
            SelfImpactExtraZMomentum = 25000,
        },
    },
    {
        name="Spinfusor MK-X",
        changes={
            Damage = 660,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 28,
            ReloadTime = 1.5,
            SelfImpactExtraZMomentum = 25000,
        },
    },
    {
        name="Heavy Twinfusor",
        changes={
            Damage = 440,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 36,
            ImpactMomentum = 85000,
            SelfImpactMomentumMultiplier = 0.5,
            SelfImpactExtraZMomentum = 45000,
            ReloadTime = 1.9,
        },
    },
    {
        name="X1 LMG",
        changes={
            Damage = 75,
            ProjectileInheritance = 0,
            ClipAmmo = 80,
            SpareAmmo = 460,
            ReloadTime = 1.925,
            FireInterval = 0.1,
            SpinupTime = 0.5,
        },
    },
    {
        name="Heavy AP Grenade",
        changes={
            Damage = 1500,
            ExplosiveRadius = 624,
            SpareAmmo = 2,
        },
    },
    {
        name="Heavy AP-XL",
        changes={
            Damage = 1300,
            ExplosiveRadius = 696,
            SpareAmmo = 2,
        },
    },
    {
        name="Spinfusor Disk",
        changes={
            Damage = 650,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 2,
        },
    },
    {
        name="Regen Pack",
        valueMods={
            RegenTimeBuff = 0.14,
        },
    },
}

-- gotylike/definitions/Doombringer.lua
----------------------------------------
doombringerClassDef = {
    ootbClass="Heavy",
    armorClass="Doombringer",
    weapons={
        "Chain Gun",
        "Chain Cannon",
        "Heavy Bolt Launcher",
        "Saber Launcher",
        "Titan Launcher",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "Frag Grenade",
        "Mines",
    },
    packs={
        "Forcefield",
    },
    skins={
        "Doombringer",
        "Executioner",
    },
    properties={
        HealthPool = 2300,
        RegenTime = 20,
        EnergyPool = 80,
        Mass = 130,
        RegenRate = 0.1,
        VehicleSpeedInheritance = 0.75,
    },
    armorValueMods={
        -- Doombringer Armor Upgrades
        HealthBuff = 200,
        RegenTimeBuff = 0.25,
        EnergyBuff = 10,
        HealthRegenRateBuff = 0.25,
        ExtraDeployables = 1,
    }
}
doombringerItemDefs =  {
    {
        name="Chain Gun",
        changes={
            Damage = 95,
            ProjectileSpeed = 18000,
            ProjectileMaxSpeed = 18000,
            ClipAmmo = 250,
            SpareAmmo = 250,
            ReloadTime = 1.925,
            FireInterval = 0.11,
            SpinupTime = 1.05,
            Accuracy = 0.98,
            AccuracyLossMax = 0.11,
            AccuracyCorrectionRate = 0.19,
        },
    },
    {
        name="Chain Cannon",
        changes={
            Damage = 115,
            ProjectileSpeed = 18000,
            ProjectileMaxSpeed = 18000,
            ClipAmmo = 250,
            SpareAmmo = 250,
            ReloadTime = 1.925,
            FireInterval = 0.14,
            SpinupTime = 1.05,
            Accuracy = 0.98,
            AccuracyLossMax = 0.11,
            AccuracyCorrectionRate = 0.19,
        },
    },
    {
        name="Heavy Bolt Launcher",
        changes={
            Damage = 750,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.4,
            SelfImpactExtraZMomentum = 25000,
            ImpactMomentum=90000,
            SpareAmmo = 30,
            ReloadTime = 1.7,
        },
    },
    {
        -- Because of the OOTB change to Saber logic, it can't really be reverted
        -- I'm giving it slightly reduced explosive radius to compensate for its anti-shrike advantage
        name="Saber Launcher",
        changes={
            Damage = 650,
            ExplosiveRadius = 360,
            DirectHitMultiplier = 1.25,
            ProjectileSpeed = 650,
            ProjectileMaxSpeed = 2800,
            ImpactMomentum = 55000,
            SelfImpactMomentumMultiplier = 1.2,
            SpareAmmo = 20,
            ReloadTime = 1.7,
            FireInterval = 0.5,
        },
    },
    {
        name="Titan Launcher",
        changes={
            Damage = 650,
            ExplosiveRadius = 450,
            DirectHitMultiplier = 1.25,
            ProjectileSpeed = 3000,
            ProjectileMaxSpeed = 8000,
            ImpactMomentum  = 65000,
            SelfImpactMomentumMultiplier = 1.2,
            SpareAmmo = 20,
            ReloadTime = 1.7,
            FireInterval = 0.5,
            CollisionSize = 35,
        },
    },
    {
        name="Frag Grenade",
        changes={
            Damage = 900,
            ExplosiveRadius = 572,
            SpareAmmo = 2,
            FuseTimer = 1.5,
        },
    },
    {
        name="Mine",
        changes={
            Damage = 700,
            ExplosiveRadius = 400,
            SpareAmmo = 2,
            MineCollisionCylinderRadius = 180,
            MineCollisionCylinderHeight = 72,
        },
    },
    {
        name="Forcefield",
        changes={
            ForcefieldMinDamage = 100,
            ForcefieldMaxDamage = 800,
            ForcefieldMinDamageSpeed = 100,
            ForcefieldMaxDamageSpeed = 1800,
        },
    },
}

-- gotylike/definitions/Brute.lua
----------------------------------------
bruteClassDef = {
    ootbClass="Heavy",
    armorClass="Brute",
    weapons={
        "Heavy Spinfusor",
        "Devastator Spinfusor",
        "Gladiator",
        "Automatic Shotgun",
        "The Hammer",
        "Nova Colt",
        "Plasma Cannon",
        "EFG",
        {class="Light", name="Shocklance"},
        {class="Medium", name="Long Range Repair Tool"}, -- Dummy tertiary weapon
    },
    beltItems={
        "Fractal Grenade",
        "Extended Fractal",
        "Light Sticky Grenade",
    },
    packs={
        "Heavy Shield Pack",
        "Heavy Energy Pack",
        "Survival Pack",
    },
    skins={
        "Brute",
        "Crusher",
    },
    properties={
        HealthPool = 2400,
        RegenTime = 20,
        Mass = 130,
        RegenRate = 0.1,
        EnergyPool = 80,
        VehicleSpeedInheritance = 0.75,
    },
    armorValueMods={
        -- Brute Armor Upgrades
        HealthBuff = 200,
        RegenTimeBuff = 0.25,
        EnergyBuff = 5,
        HealthRegenRateBuff = 0.25,
    }
}
bruteItemDefs = {
    {
        name="Heavy Spinfusor",
        changes={
            Damage = 750,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 30,
            ImpactMomentum = 90000,
            SelfImpactExtraZMomentum = 25000,
            ReloadTime = 1.8,
        },
    },
    {
        name="Devastator Spinfusor",
        changes={
            Damage = 700,
            DirectHitMultiplier = 1.72,
            ProjectileInheritance = 0.5,
            SpareAmmo = 30,
            ImpactMomentum = 90000,
            ReloadTime = 1.8,
            ExplosiveRadius = 390,
        },
    },
    {
        name="Gladiator",
        changes={
            Damage = 800,
            ExplosiveRadius = 200,
            DirectHitMultiplier = 1.4,
            SpareAmmo = 20,
            ReloadTime = 1.4,
        },
    },
    {
        name="Nova Colt",
        changes={
            HoldToFire = false,
            ClipAmmo = 6,
            SpareAmmo = 72,
            LowAmmoCutoff = 1,
            ReloadTime = 1.4,
            -- Fire rate corresponding to ping-dependent GOTY rate of 0.24 for someone with ping 30
            FireInterval = 0.27,
            Damage = 190,
            HitscanRange = 10000,
            MinDamageProportion = 0.65,
            MaxDamageRangeProportion = 0.2,
            MinDamageRangeProportion = 0.4,
            Accuracy = 0.98,
            AccuracyLossOnShot = 0.45,
            AccuracyLossMax = 0.1,
            AccuracyCorrectionRate = 0.38,
        },
    },
    {
        name="Auto Shotgun",
        changes={
            Damage = 50,
            ShotgunShotCount = 8,
            ClipAmmo = 8,
            SpareAmmo = 60,
            HitscanRange = 3000,
            ReloadTime = 1.35,
            Accuracy = 0.85,
            AccuracyLossMax = 0.3,
            AccuracyLossOnShot = 0.0,
            AccuracyCorrectionRate = 0.18,
            ShotgunUseGOTYSpread = true,
        },
    },
    {
        name="The Hammer",
        changes={
            Damage = 60,
            ShotgunShotCount = 8,
            ClipAmmo = 6,
            SpareAmmo = 50,
            HitscanRange = 3000,
            ReloadTime = 1.35,
            Accuracy = 0.85,
            AccuracyLossMax = 0.3,
            AccuracyLossOnShot = 0.0,
            AccuracyCorrectionRate = 0.18,
            ShotgunUseGOTYSpread = true,
        },
    },
    {
        name="Plasma Cannon",
        changes={
            Damage = 460,
            DirectHitMultiplier = 1.25,
            ExplosiveRadius = 270,
            ProjectileInheritance = 0.5,
            ProjectileSpeed = 3620,
            ProjectileMaxSpeed = 8000,
            ProjectileLifespan = 3,
            SelfImpactExtraZMomentum = 45000,
            ClipAmmo = 10,
            SpareAmmo = 60,
            ReloadTime = 2.75,
            FireInterval = 0.85,
            DamageAgainstShrikeMultiplier = 0.1,
        },
    },
    {
        name="Light Sticky Grenade",
        valueMods={
            ExtraBeltAmmo = 0,
            BeltDamageRadiusBuff = 0.1,
            BeltArmorPenetrationBuff = 0.2,
        },
    },
    {
        name="Fractal Grenade",
        changes={
            Damage = 370, -- Reduced final explosion damage
            ExplosiveRadius = 520,
            SpareAmmo = 2,
            ProjectileSpeed = 1200,
            ImpactMomentum = 40000,
            FractalDuration = 4.5,
            FractalShardInterval = 0.2,
            FractalAscentTime = 1,
            FractalAscentHeight = 90,
            FractalShardDistance = 900,
            FractalShardHeight = 100,
            FractalShardDamage = 370,
            FractalShardDamageRadius = 300,
            MinDamageProportion = 1,
            MaxDamageRangeProportion = 0.5,
            MinDamageRangeProportion = 0.9,
        },
    },
    {
        name="Extended Fractal Grenade",
        changes={
            Damage = 350, -- Reduced final explosion damage
            ExplosiveRadius = 520,
            SpareAmmo = 2,
            ProjectileSpeed = 1200,
            ImpactMomentum = 40000,
            FractalDuration = 5.5,
            FractalShardInterval = 0.2,
            FractalAscentTime = 1,
            FractalAscentHeight = 90,
            FractalShardDistance = 900,
            FractalShardHeight = 100,
            FractalShardDamage = 350,
            FractalShardDamageRadius = 300,
            MinDamageProportion = 1,
            MaxDamageRangeProportion = 0.5,
            MinDamageRangeProportion = 0.9,
        },
    },
    {
        name="Survival Pack",
        valueMods={
            HealthBuff = 200,
            EnergyBuff = 15,
            WalkSpeedBuff = 0.25,
            EnergyRegenRateBuff = 0.15,
        },
    },
    {
        name="Heavy Energy Pack",
        valueMods={
            EnergyBuff = 35,
        },
    },
    {
        name="Heavy Shield Pack",
        changes={
            PackSustainedEnergyCost = 4.25,
        },
        valueMods={
            ShieldPackBuff = 0.036,
        },
    },
}

-- gotylike/classes.lua
----------------------------------------

local function applyCustomClass(className, class)
    local classDef = class.class
    addClass(className, classDef.ootbClass, classDef.armorClass,
                   classDef.weapons, classDef.beltItems, classDef.packs,
                   classDef.skins)
    Classes.setValueMods(classDef.armorClass, valueModsListDefConverter(classDef.armorValueMods))
    for propName, propVal in pairs(classDef.properties) do
        Classes.setProperty(classDef.armorClass, Classes.Properties[propName], propVal)
    end
end

local function applyClassItemDefs(class)
    for modIdx, modDef in pairs(class.items) do
        local item = {
            class=modDef.class or class.class.ootbClass,
            name=modDef.name
        }
        -- Apply each property
        if modDef.changes ~= nil then
            for changeProp, changeVal in pairs(modDef.changes) do
                Items.setProperty(item.class, item.name, Items.Properties[changeProp], changeVal)
            end
        end
        -- Apply each valuemod
        if modDef.valueMods ~= nil then
            Items.setValueMods(item.class, item.name,
                               valueModsListDefConverter(modDef.valueMods))
        end
    end
end

applyCustomClass("Pathfinder", pathfinderClassDef)
applyClassItemDefs(pathfinderItemsDef)

applyCustomClass("Infiltrator", infiltratorClassDef)
applyClassItemDefs(infiltratorItemDefs)

applyCustomClass("Sentinel", sentinelClassDef)
applyClassItemDefs(sentinelItemDefs)

applyCustomClass("Soldier", soldierClassDef)
applyClassItemDefs(soldierItemDefs)

applyCustomClass("Raider", raiderClassDef)
applyClassItemDefs(raiderItemDefs)

applyCustomClass("Technician", technicianClassDef)
applyClassItemDefs(technicianItemDefs)

applyCustomClass("Juggernaut", juggernautClassDef)
applyClassItemDefs(juggernautItemDefs)

applyCustomClass("Doombringer", doombringerClassDef)
applyClassItemDefs(doombringerItemDefs)

applyCustomClass("Brute", bruteClassDef)
applyClassItemDefs(bruteItemDefs)

-- gotylike/definitions/GravCycle.lua
----------------------------------------
gravCycleVehicleDef = {
    properties = {
        HealthPool = 1400,
        EnergyPool = 100,
        EnergyRechargeRate = 13,
        BoostEnergyCost = 20,
        BoostMultiplier = 1.5,

        MaxSpeed = 2500,
        MaxDivingSpeedMultiplier = 1.2,

        MinCrashDamageSpeed = 400,
        MaxCrashDamageSpeed = 2400,
        MinCrashDamage = 200,
        MaxCrashDamage = 2000,
        RamMinSpeed = 800,
        RamMaxDamageSpeed = 1900,
        RamMinDamage = 100,
        RamMaxDamage = 2400,
    },
}
gravCycleVehicleWeaponsDef = {
    {
        name="Grav Cycle",
        changes={
            Damage = 250,
            ExplosiveRadius = 200,
            ProjectileSpeed = 4000,
            ProjectileMaxSpeed = 4000,
            ImpactMomentum = 15000,
            CollisionSize = 42,
            DamageAgainstShrikeMultiplier = 2.5,

            ClipAmmo = 8,
            ReloadTime = 4.0,
            FireInterval = 0.15,

            MaxDamageRangeProportion = 0.5,
            MinDamageRangeProportion = 0.9,
            MinDamageProportion = 0.7
        },
    }
}

-- gotylike/definitions/Beowulf.lua
----------------------------------------
beowulfVehicleDef = {
    properties = {
        HealthPool = 8000,
        EnergyPool = 80,
        EnergyRechargeRate = 8,
        BoostEnergyCost = 20,
        BoostMultiplier = 1.25,

        MaxSpeed = 1000,
        MaxDivingSpeedMultiplier = 1.1,

        MinCrashDamageSpeed = 1000,
        MaxCrashDamageSpeed = 2100,
        MinCrashDamage = 100,
        MaxCrashDamage = 400,
        RamMinSpeed = 800,
        RamMaxDamageSpeed = 1600,
        RamMinDamage = 500,
        RamMaxDamage = 1000,
    },
}
beowulfVehicleWeaponsDef = {
    {
        name="Beowulf Cannon",
        changes={
            Damage = 1000,
            DirectHitMultiplier = 2,
            ExplosiveRadius = 750,
            ProjectileSpeed = 9000,
            ProjectileMaxSpeed = 20000,
            ImpactMomentum = 100000,
            CollisionSize = 42,
            DamageAgainstShrikeMultiplier = 2.5,

            FireInterval = 4.0,

            MaxDamageRangeProportion = 0.5,
            MinDamageRangeProportion = 0.9,
            MinDamageProportion = 0.5
        },
    },
    {
        name="Beowulf Chain",
        changes={
            Damage = 100,
            ProjectileSpeed = 18000,
            ProjectileMaxSpeed = 18000,
            CollisionSize = 50,
            DamageAgainstShrikeMultiplier = 0.65,

            ClipAmmo = 100,
            ReloadTime = 4.0,
            FireInterval = 0.11,

            Accuracy = 0.98,
            AccuracyLossOnShot = 0,
            AccuracyCorrectionRate = 0.19,
            AccuracyLossMax = 0.11,

            MaxDamageRangeProportion = 0.5,
            MinDamageRangeProportion = 1.0,
            MinDamageProportion = 0.75
        },
    }
}

-- gotylike/definitions/Shrike.lua
----------------------------------------
shrikeVehicleDef = {
    properties = {
        HealthPool = 3200,
        EnergyPool = 70,
        EnergyRechargeRate = 10,
        BoostEnergyCost = 20,
        BoostMultiplier = 1.5,

        MaxSpeed = 2400,
        MaxDivingSpeedMultiplier = 1.2,

        MinCrashDamageSpeed = 400,
        MaxCrashDamageSpeed = 2400,
        MinCrashDamage = 200,
        MaxCrashDamage = 2000,
        RamMinSpeed = 200,
        RamMaxDamageSpeed = 2200,
        RamMinDamage = 75,
        RamMaxDamage = 1800,
    },
}

shrikeVehicleWeaponsDef = {
    {
        name="Shrike",
        changes={
            Damage = 350,
            ExplosiveRadius = 320,
            ImpactMomentum = 85000,
            ProjectileLifespan = 10,
            ProjectileSpeed = 8500,
            ProjectileMaxSpeed = 8500,
            CollisionSize = 42,
            DamageAgainstShrikeMultiplier = 2.5,

            ClipAmmo = 4,
            BurstShotCount = 4,
            ReloadTime = 4.0,
            FireInterval = 0.25,

            MaxDamageRangeProportion = 0.5,
            MinDamageRangeProportion = 0.9,
            MinDamageProportion = 0.7
        },
    }
}

-- gotylike/vehicles.lua
----------------------------------------
local function applyVehicleDefs(vehName, vehicle)
    local vehDef = vehicle.vehicle
    for propName, propVal in pairs(vehDef.properties) do
        Vehicles.setProperty(vehName, Vehicles.Properties[propName], propVal)
    end
end

local function applyVehicleWeaponDefs(vehicle)
    for idx, vehicleWep in pairs(vehicle.weapons) do
        for propName, propVal in pairs(vehicleWep.changes) do
            VehicleWeapons.setProperty(vehicleWep.name, VehicleWeapons.Properties[propName], propVal)
        end
    end
end

applyVehicleDefs("GravCycle", gravCycleVehicleDef)
applyVehicleWeaponDefs(gravCycleVehicleWeaponsDef)

applyVehicleDefs("Beowulf", beowulfVehicleDef)
applyVehicleWeaponDefs(beowulfVehicleWeaponsDef)

applyVehicleDefs("Shrike", shrikeVehicleDef)
applyVehicleWeaponDefs(shrikeVehicleWeaponsDef)

ServerSettings.GameSettingMode = ServerSettings.GameSettingModes.GOTY
----------------------------------------
