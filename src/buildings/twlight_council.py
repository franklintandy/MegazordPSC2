from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))


class TwilightCouncil():
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    async def build_twilight_council(self):
        if (self.bot.structures(UnitTypeId.PYLON).amount > 0):
            pylon = self.bot.structures(UnitTypeId.PYLON).ready.random
            if self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready:
                # If we have no twilight council, build one
                if not self.bot.structures(UnitTypeId.TWILIGHTCOUNCIL):
                    if (
                        self.bot.can_afford(UnitTypeId.TWILIGHTCOUNCIL)
                        and self.bot.already_pending(UnitTypeId.TWILIGHTCOUNCIL) == 0
                    ):
                        await self.bot.build(UnitTypeId.TWILIGHTCOUNCIL, near=pylon)

    def research_charge(self):
        if (
            self.bot.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and self.bot.can_afford(AbilityId.RESEARCH_CHARGE)
            and self.bot.already_pending_upgrade(UpgradeId.CHARGE) == 0
        ):
            twilightCouncil = self.bot.structures(
                UnitTypeId.TWILIGHTCOUNCIL).ready.first
            twilightCouncil.research(UpgradeId.CHARGE)

    def research_blink(self):
        if (
            self.bot.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
            and self.bot.can_afford(AbilityId.RESEARCH_BLINK)
            and self.bot.already_pending_upgrade(UpgradeId.BLINKTECH) == 0
        ):
            twilightCouncil = self.bot.structures(
                UnitTypeId.TWILIGHTCOUNCIL).ready.first
            twilightCouncil.research(UpgradeId.BLINKTECH)
