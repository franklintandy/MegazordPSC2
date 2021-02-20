from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))


class CyberneticsCore():
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    async def build_cybercore_after_gateway(self):
        pylon = self.bot.structures(UnitTypeId.PYLON).ready.random
        if self.bot.structures(UnitTypeId.GATEWAY).ready:
            # If we have no cyber core, build one
            if not self.bot.structures(UnitTypeId.CYBERNETICSCORE):
                if (
                    self.bot.can_afford(UnitTypeId.CYBERNETICSCORE)
                    and self.bot.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                ):
                    await self.bot.build(UnitTypeId.CYBERNETICSCORE, near=pylon)

    def research_warpgate(self):
        if (
            self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.bot.can_afford(AbilityId.RESEARCH_WARPGATE)
            and self.bot.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
        ):
            ccore = self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            ccore.research(UpgradeId.WARPGATERESEARCH)

    def research_air_weapons(self, level=1):
        switcher = {
            1: UpgradeId.PROTOSSAIRWEAPONSLEVEL1,
            2: UpgradeId.PROTOSSAIRWEAPONSLEVEL2,
            3: UpgradeId.PROTOSSAIRWEAPONSLEVEL3,
        }

        upgrade = switcher.get(level, None)
        if (upgrade is None):
            return

        if (
            self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.bot.can_afford(AbilityId.RESEARCH_PROTOSSAIRWEAPONS)
            and self.bot.already_pending_upgrade(upgrade) == 0
        ):
            ccore = self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            ccore.research(upgrade)

    def research_air_armor(self, level=1):
        switcher = {
            1: UpgradeId.PROTOSSAIRARMORSLEVEL1,
            2: UpgradeId.PROTOSSAIRARMORSLEVEL2,
            3: UpgradeId.PROTOSSAIRARMORSLEVEL3,
        }

        upgrade = switcher.get(level, None)
        if (upgrade is None):
            return

        if (
            self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.bot.can_afford(AbilityId.RESEARCH_BLINK)
            and self.bot.already_pending_upgrade(upgrade) == 0
        ):
            ccore = self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            ccore.research(upgrade)
