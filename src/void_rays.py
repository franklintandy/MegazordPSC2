from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.units import Units
from sc2.unit import Unit
from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2 import Race, Difficulty

from base.economy import Economy
from buildings.cybernetics_core import CyberneticsCore
from buildings.warpgate import Warpgate
from buildings.stargate import Stargate

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

class VoidRayRushBot(sc2.BotAI):
    def __init__(self):
        # Initialize inherited class
        sc2.BotAI.__init__(self)

        self.economy = Economy(self)
        self.ccore = CyberneticsCore(self)
        self.warpgate = Warpgate(self)
        self.stargate = Stargate(self)

    def chronoboosts(self, nexus):
        # Chrono nexus if cybercore is not ready, else chrono cybercore
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready:
            if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and not nexus.is_idle:
                if nexus.energy >= 50:
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
        else:
            ccore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if not ccore.has_buff(BuffId.CHRONOBOOSTENERGYCOST) and not ccore.is_idle:
                if nexus.energy >= 50:
                    nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore)

    def attack_with_all(self):
        if self.units(UnitTypeId.VOIDRAY).amount > 1:
            targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
            for zealot in self.units(UnitTypeId.ZEALOT).ready.idle:
                if targets:
                    target = targets.closest_to(zealot)
                    zealot.attack(target)
                else:
                    zealot.attack(self.enemy_start_locations[0])
            for stalker in self.units(UnitTypeId.STALKER).ready.idle:
                if targets:
                    target = targets.closest_to(stalker)
                    stalker.attack(target)
                else:
                    stalker.attack(self.enemy_start_locations[0])
            for vr in self.units(UnitTypeId.VOIDRAY):
                # Activate charge ability if the void ray just attacked
                if vr.weapon_cooldown > 0:
                    vr(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)
                if targets:
                    target = targets.closest_to(vr)
                    vr.attack(target)
                else:
                    vr.attack(self.enemy_start_locations[0])

    async def on_step(self, iteration):
        await self.distribute_workers()

        if not self.townhalls.ready:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
            return
        else:
            nexus = self.townhalls.ready.random

        self.chronoboosts(nexus)

        await self.economy.build_pylons_at(nexus)

        self.economy.build_probes_at(nexus)

        self.economy.build_gas()

        if self.structures(UnitTypeId.GATEWAY).amount < 2 and self.structures(UnitTypeId.WARPGATE).amount < 6:
            await self.warpgate.build_gateway()

        if self.structures(UnitTypeId.GATEWAY).amount > 0:
            await self.ccore.build_cybercore_after_gateway()

        if self.structures(UnitTypeId.GATEWAY).amount <= 2 and self.structures(UnitTypeId.STARGATE).amount < 2:
            await self.stargate.build_stargate()

        if self.structures(UnitTypeId.PYLON).ready:
            unit = 'zealot' if (iteration % 2 == 0) else 'stalker'  
            await self.warpgate.warp_unit(self.structures(UnitTypeId.PYLON).ready.random, unit)

        self.ccore.research_warpgate()

        self.warpgate.morph_warpgates()

        self.stargate.train_void_rays()

        self.attack_with_all()


def main():
    sc2.run_game(
        sc2.maps.get("AcropolisLE"),
        [Bot(Race.Protoss, VoidRayRushBot()),
         Computer(Race.Protoss, Difficulty.Easy)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
