import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import random
import functools 

import sc2
from sc2 import Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.player import Bot, Computer


class CannonRushBot(sc2.BotAI):
    async def on_step(self, iteration):
        if iteration == 0:
            self.already_assigned = 0
            await self.chat_send("(probe)(colonize)(probe)(attack)(gg)")
            # self._find_expansion_locations()

        if not self.townhalls:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
            return
        # else:
            # nexus = self.townhalls.random
        for nexus in self.townhalls:
            # Make probes until we have 16 total
            if nexus.is_idle:
                await self.distribute_workers()
                if self.can_afford(UnitTypeId.PROBE):
                    nexus.train(UnitTypeId.PROBE)

            # If we have no pylon, build one near starting nexus
            # elif not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
            elif (len(self.structures(UnitTypeId.PYLON)) + self.already_pending(UnitTypeId.PYLON)) <= 3:
                if self.can_afford(UnitTypeId.PYLON):
                    # print('Building pylon {}'.format(len(self.structures(UnitTypeId.PYLON)) + self.already_pending(UnitTypeId.PYLON)))
                    await self.build(UnitTypeId.PYLON, near=nexus)

        if self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) < 14:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()
        limit = 100
        lista = [1 if worker.is_attacking else 0 for worker in self.workers]
        self.already_assigned = functools.reduce(lambda a,b: a+b, lista)

        if len(self.workers) > limit + self.already_assigned:
            for worker in self.workers:
                if not worker.is_attacking and len(self.workers) - self.already_assigned > limit:
                    if self.enemy_start_locations[0]: worker.attack(self.enemy_start_locations[0])
                    elif self.enemy_structures[0]: worker.attack(self.enemy_structures[0])
                    else: worker.attack(self.enemy_units[0])
            return

            # # If we have no forge, build one near the pylon that is closest to our starting nexus
            # if not self.structures(UnitTypeId.FORGE):
            #     pylon_ready = self.structures(UnitTypeId.PYLON).ready
            #     if pylon_ready:
            #         if self.can_afford(UnitTypeId.FORGE):
            #             await self.build(UnitTypeId.FORGE, near=pylon_ready.closest_to(nexus))
            #             return

            # # If we have more than 2 pylons, build one at the enemy base
            # if self.structures(UnitTypeId.PYLON).amount > 2:
            #     if self.can_afford(UnitTypeId.PYLON):
            #         pos = self.enemy_start_locations[0].towards(self.game_info.map_center, random.randrange(8, 15))
            #         await self.build(UnitTypeId.PYLON, near=pos)
            #         return

            # # If we have no cannons but at least 2 completed pylons, automatically find a placement location and build them near enemy start location
            # if not self.structures(UnitTypeId.PHOTONCANNON):
            #     if self.structures(UnitTypeId.PYLON).ready.amount >= 5 and self.can_afford(UnitTypeId.PHOTONCANNON):
            #         pylon = self.structures(UnitTypeId.PYLON).closer_than(40, self.enemy_start_locations[0]).random
            #         await self.build(UnitTypeId.PHOTONCANNON, near=pylon)

            # # Decide if we should make pylon or cannons, then build them at random location near enemy spawn
            # if self.can_afford(UnitTypeId.PYLON) and self.can_afford(UnitTypeId.PHOTONCANNON):
            #     # Ensure "fair" decision
            #     for _ in range(50):
            #         pos = self.enemy_start_locations[0].random_on_distance(random.randrange(5, 12))
            #         building = UnitTypeId.PHOTONCANNON if self.state.psionic_matrix.covers(pos) else UnitTypeId.PYLON
            #         await self.build(building, near=pos)


def main():
    sc2.run_game(
        sc2.maps.get("(2)CatalystLE"),
        # [Bot(Race.Protoss, CannonRushBot(), name="ProbeMaster"), Computer(Race.Protoss, Difficulty.Medium)],
        [Bot(Race.Protoss, CannonRushBot(), name="ProbeMaster"), Computer(Race.Protoss, Difficulty.VeryHard)],
        realtime=False,
        save_replay_as="ProbeSwarm_vs_Protos_HIGH.SC2Replay"
    )


if __name__ == "__main__":
    main()
