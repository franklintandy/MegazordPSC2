from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

class Warpgate(sc2.BotAI):
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    async def build_gateway(self):
        if self.bot.structures(UnitTypeId.PYLON).ready:
            pylon = self.bot.structures(UnitTypeId.PYLON).ready.random
            if (self.bot.can_afford(UnitTypeId.GATEWAY)):
                await self.bot.build(UnitTypeId.GATEWAY, near=pylon)

    # Morph to warp gate when research is complete
    def morph_warpgates(self):
        for gateway in self.bot.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.bot.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 1:
                gateway(AbilityId.MORPH_WARPGATE)

    async def warp_unit(self, pylon, unitType):
        warpgate_units = {
            'zealot': {'abilityId': AbilityId.WARPGATETRAIN_ZEALOT, 'unitId': UnitTypeId.ZEALOT},
            'stalker': {'abilityId': AbilityId.WARPGATETRAIN_STALKER, 'unitId': UnitTypeId.STALKER},
            'sentry': {'abilityId': AbilityId.WARPGATETRAIN_SENTRY, 'unitId': UnitTypeId.SENTRY},
            'dark_templar': {'abilityId': AbilityId.WARPGATETRAIN_DARKTEMPLAR, 'unitId': UnitTypeId.DARKTEMPLAR},
            'high_templar': {'abilityId': AbilityId.WARPGATETRAIN_HIGHTEMPLAR, 'unitId': UnitTypeId.HIGHTEMPLAR},
        }

        selected_unit = warpgate_units.get(unitType, None)
        if (selected_unit is None):
            return

        abilityId = selected_unit.get('abilityId')
        unitId = selected_unit.get('unitId')

        for warpgate in self.bot.structures(UnitTypeId.WARPGATE).ready:
            abilities = await self.bot.get_available_abilities(warpgate)
            if abilityId in abilities:
                pos = pylon.position.to2.random_on_distance(4)
                placement = await self.bot.find_placement(abilityId, pos, placement_step=1)
                if placement is None:
                    return
                warpgate.warp_in(unitId, placement)
