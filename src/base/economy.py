from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

#### Resources Management Class ####

class Economy():
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    # build pylons if low on supply
    async def build_pylons_at(self, nexus):
        if self.bot.supply_left < 2 and self.bot.already_pending(UnitTypeId.PYLON) <= 1:
            # Always check if you can afford something before you build it
            if self.bot.can_afford(UnitTypeId.PYLON):
                await self.bot.build(UnitTypeId.PYLON, near=nexus)
            return

    # build up to 22 probes per Nexus
    def build_probes_at(self, nexus):
        if self.bot.supply_workers + self.bot.already_pending(UnitTypeId.PROBE) < self.bot.townhalls.amount * 22 and nexus.is_idle:
            if self.bot.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)

    # Ensures every base has both gases built
    def build_gas(self):
        for nexus in self.bot.townhalls.ready:
            vgs = self.bot.vespene_geyser.closer_than(15, nexus)
            for vg in vgs:
                if not self.bot.can_afford(UnitTypeId.ASSIMILATOR):
                    break
                worker = self.bot.select_build_worker(vg.position)
                if worker is None:
                    break
                if not self.bot.gas_buildings or not self.bot.gas_buildings.closer_than(1, vg):
                    worker.build(UnitTypeId.ASSIMILATOR, vg)
                    worker.stop(queue=True)
