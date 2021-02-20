from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))


class RoboticsFacility():
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    async def build_robotics_facility(self):
        if (self.bot.structures(UnitTypeId.PYLON).ready and self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready):
            pylon = self.bot.structures(UnitTypeId.PYLON).ready.random
            if (self.bot.can_afford(UnitTypeId.ROBOTICSFACILITY)):
                await self.bot.build(UnitTypeId.ROBOTICSFACILITY, near=pylon)

    def train_immortals(self):
        for sg in self.bot.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
            if self.bot.can_afford(UnitTypeId.IMMORTAL):
                sg.train(UnitTypeId.IMMORTAL)

    def train_observers(self):
        for sg in self.bot.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
            if self.bot.can_afford(UnitTypeId.OBSERVER):
                sg.train(UnitTypeId.OBSERVER)

    def train_warp_prisms(self):
        for sg in self.bot.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
            if self.bot.can_afford(UnitTypeId.WARPPRISM):
                sg.train(UnitTypeId.WARPPRISM)

    def train_colossus(self):
        if (self.bot.structures(UnitTypeId.ROBOTICSBAY).ready):
            for sg in self.bot.structures(UnitTypeId.ROBOTICSFACILITY).ready.idle:
                if self.bot.can_afford(UnitTypeId.COLOSSUS):
                    sg.train(UnitTypeId.COLOSSUS)
