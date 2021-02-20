from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

class Stargate():
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    async def build_stargate(self):
        if (self.bot.structures(UnitTypeId.PYLON).ready and self.bot.structures(UnitTypeId.CYBERNETICSCORE).ready):
            pylon = self.bot.structures(UnitTypeId.PYLON).ready.random
            # Build up to 4 gates
            if (self.bot.can_afford(UnitTypeId.STARGATE)):
                await self.bot.build(UnitTypeId.STARGATE, near=pylon)

    def train_void_rays(self):
        for sg in self.bot.structures(UnitTypeId.STARGATE).ready.idle:
            if self.bot.can_afford(UnitTypeId.VOIDRAY):
                sg.train(UnitTypeId.VOIDRAY)

    def train_phoenixes(self):
        for sg in self.bot.structures(UnitTypeId.STARGATE).ready.idle:
            if self.bot.can_afford(UnitTypeId.PHOENIX):
                sg.train(UnitTypeId.PHOENIX)

    def train_carriers(self):
        if (self.bot.structures(UnitTypeId.FLEETBEACON).ready):
            for sg in self.bot.structures(UnitTypeId.STARGATE).ready.idle:
                if self.bot.can_afford(UnitTypeId.CARRIER):
                    sg.train(UnitTypeId.CARRIER)

    def train_tempests(self):
        if (self.bot.structures(UnitTypeId.FLEETBEACON).ready):
            for sg in self.bot.structures(UnitTypeId.STARGATE).ready.idle:
                if self.bot.can_afford(UnitTypeId.TEMPEST):
                    sg.train(UnitTypeId.TEMPEST)
