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
from loguru import logger



class ProbeMasterBot(sc2.BotAI):
    async def on_step(self, iteration):
        if iteration == 0:
            self.lastConstruction = None
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
        # Expand condition
        if self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) < 14:
            if self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()

        for nexus in self.townhalls:
            # Make probes until we have 16 per nexus
            if nexus.surplus_harvesters < 6:
                if self.can_afford(UnitTypeId.PROBE):
                    nexus.train(UnitTypeId.PROBE)

        if self.minerals > 800:
            for nexus in self.townhalls:

                # Build assimilators
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                        worker.build(UnitTypeId.ASSIMILATOR, vg)
                        worker.stop(queue=True)


                near_pylons = self.structures(UnitTypeId.PYLON).closer_than(20, nexus)
                near_cannons = self.structures(UnitTypeId.PHOTONCANNON).closer_than(20, nexus)
                # If we have no pylon, build one near starting nexus
                # elif not self.structures(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                # logger.info('Near Pylons {} '.format(near_pylons))
                # logger.info('Near Cannons {} '.format(near_cannons))
                # if len(near_cannons) <= 3 and len(near_pylons) > 0:
                    # if self.can_afford(UnitTypeId.PHOTONCANNON):
                        # pylon = self.structures(UnitTypeId.PYLON).closer_than(40, self.enemy_start_locations[0]).random
                        # pylon = near_pylons.random
                        # cannon_pos = await self.find_placement(UnitTypeId.PHOTONCANNON, near=pylon.position)
                        # if self.state.psionic_matrix.covers(cannon_pos):
                        # logger.info('Building cannon near {} at {} '.format(pylon.position, cannon_pos.position))
                        # await self.build(UnitTypeId.PHOTONCANNON, near=cannon_pos.position)

                if len(near_pylons) <= 3:
                    if self.can_afford(UnitTypeId.PYLON):
                        # print('Building pylon {}'.format(len(self.structures(UnitTypeId.PYLON)) + self.already_pending(UnitTypeId.PYLON)))
                        pylon_pos = await self.find_placement(UnitTypeId.PYLON, near=nexus.position)
                        logger.info('Building pylon at {} near nexus at {} '.format(pylon_pos, nexus.position))
                        await self.build(UnitTypeId.PYLON, near=pylon_pos)
                # If we have no cannons but at least 2 completed pylons, automatically find a placement location and build them near enemy start location


        if len(self.workers.idle) > 0:
            await self.distribute_workers()
        # limit = 100
        # lista = [1 if worker.is_attacking else 0 for worker in self.workers]
        # self.already_assigned = functools.reduce(lambda a,b: a+b, lista)

        # if len(self.workers) > limit + self.already_assigned:
        #     for worker in self.workers:
        #         if not worker.is_attacking and len(self.workers) - self.already_assigned > limit:
        #             if self.enemy_start_locations[0]: worker.attack(self.enemy_start_locations[0])
        #             elif self.enemy_structures[0]: worker.attack(self.enemy_structures[0])
        #             else: worker.attack(self.enemy_units[0])
        #     return

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
        # [Bot(Race.Protoss, ProbeMasterBot(), name="ProbeMaster"), Computer(Race.Protoss, Difficulty.Medium)],
        [Bot(Race.Protoss, ProbeMasterBot(), name="ProbeMaster"), Computer(Race.Protoss, Difficulty.VeryHard)],
        realtime=False,
        save_replay_as="ProbeSwarm_vs_Protos_HIGH.SC2Replay"
    )


if __name__ == "__main__":
    main()
