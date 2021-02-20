from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

class RoboticsBay():
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    async def build_robotics_bay(self):
        if self.bot.structures(UnitTypeId.ROBOTICSFACILITY).ready:
            pylon = self.bot.structures(UnitTypeId.PYLON).ready.random
            # If we have no robotics bay, build one
            if not self.bot.structures(UnitTypeId.ROBOTICSBAY):
                if (
                    self.bot.can_afford(UnitTypeId.ROBOTICSBAY)
                    and self.bot.already_pending(UnitTypeId.ROBOTICSBAY) == 0
                ):
                    await self.bot.build(UnitTypeId.ROBOTICSBAY, near=pylon)

    # Colossus upgrade
    def research_thermal_lance(self):
        if (
            self.bot.structures(UnitTypeId.ROBOTICSBAY).ready
            and self.bot.can_afford(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE)
            and self.bot.already_pending_upgrade(UpgradeId.CHARGE) == 0
        ):
            roboBay = self.bot.structures(UnitTypeId.ROBOTICSBAY).ready.first
            roboBay.research(UpgradeId.EXTENDEDTHERMALLANCE)

    # Observers upgrade
    def research_boosters(self):
        if (
            self.bot.structures(UnitTypeId.ROBOTICSBAY).ready
            and self.bot.can_afford(AbilityId.RESEARCH_GRAVITICBOOSTER)
            and self.bot.already_pending_upgrade(UpgradeId.OBSERVERGRAVITICBOOSTER) == 0
        ):
            roboBay = self.bot.structures(UnitTypeId.ROBOTICSBAY).ready.first
            roboBay.research(UpgradeId.OBSERVERGRAVITICBOOSTER)

    # Warp prisms upgrade
    def research_gravitic_drive(self):
        if (
            self.bot.structures(UnitTypeId.ROBOTICSBAY).ready
            and self.bot.can_afford(AbilityId.RESEARCH_GRAVITICDRIVE)
            and self.bot.already_pending_upgrade(UpgradeId.GRAVITICDRIVE) == 0
        ):
            roboBay = self.bot.structures(UnitTypeId.ROBOTICSBAY).ready.first
            roboBay.research(UpgradeId.GRAVITICDRIVE)