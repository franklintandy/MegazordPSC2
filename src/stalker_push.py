import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

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

class KittingStalkers(sc2.BotAI):
    def __init__(self):
        # Initialize inherited class
        sc2.BotAI.__init__(self)
        self.proxy_built = False
        self.proxy2 = False
        self.gateway_prontos = 0

    async def on_step(self, iteration):
        await self.distribute_workers()

        if iteration == 0:
            await self.chat_send("(glhf)")

        if not self.townhalls.ready:
            # Attack with all workers if we don't have any nexuses left, attack-move on enemy spawn (doesn't work on 4 player map) so that probes auto attack on the way
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
            return
        else:
            nexus = self.townhalls.ready.random

        # Build pylon when on low supply
        if self.supply_left < 2 and self.already_pending(UnitTypeId.PYLON) == 0:
            # Always check if you can afford something before you build it
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus)
            return

        if self.workers.amount < self.townhalls.amount * 22 and nexus.is_idle:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)

        elif self.structures(UnitTypeId.PYLON).amount < 5 and self.already_pending(UnitTypeId.PYLON) == 0:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus.position.towards(self.game_info.map_center, 5))

        if self.structures(UnitTypeId.PYLON).ready:
            proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.GATEWAY).ready:
                # If we have no cyber core, build one
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    if (
                        self.can_afford(UnitTypeId.CYBERNETICSCORE)
                        and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                    ):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            # Build up to 4 gates
            if (
                self.can_afford(UnitTypeId.GATEWAY)
                and self.structures(UnitTypeId.WARPGATE).amount + self.structures(UnitTypeId.GATEWAY).amount < 4
            ):
                await self.build(UnitTypeId.GATEWAY, near=pylon)

        # Build gas
        for nexus in self.townhalls.ready:
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

        # Research warp gate if cybercore is completed
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).ready
            and self.can_afford(AbilityId.RESEARCH_WARPGATE)
            and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
        ):
            ccore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            ccore.research(UpgradeId.WARPGATERESEARCH)

        # Morph to warp gate when research is complete
        for gateway in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.gateway_prontos >= 4:
                if self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 1:
                    gateway(AbilityId.MORPH_WARPGATE)
                    print('upgrade com:', self.gateway_prontos, 'gt-prontos')
            elif len(self.structures(UnitTypeId.GATEWAY).ready.idle) >= 4:
                print('Treinamos Stalker com:', self.gateway_prontos, 'gt-prontos')
                gateway.train(UnitTypeId.STALKER)
                self.gateway_prontos+=1


        if self.proxy_built:
            for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
                abilities = await self.get_available_abilities(warpgate)
                # all the units have the same cooldown anyway so let's just look at ZEALOT
                if AbilityId.WARPGATETRAIN_STALKER in abilities:
                    pos = proxy.position.to2.random_on_distance(4)
                    placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                    if placement is None:
                        print('cant place')
                    else:
                        warpgate.warp_in(UnitTypeId.STALKER, placement)

        # Make stalkers attack either closest enemy unit or enemy spawn location
        for stalker in self.units(UnitTypeId.STALKER).ready.idle:
            if self.units(UnitTypeId.STALKER).amount > 9:
                if stalker.health_percentage > 0.8 or stalker.shield_health_percentage > 0.5:
                    print('estou kitando:', stalker.position)
                    targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                    if targets:
                        target = targets.closest_to(stalker)
                        stalker.attack(target)
                    else:
                        stalker.attack(self.enemy_start_locations[0])
                    print('atacando com kite')
                elif stalker.is_attacking == True:
                    print('estou correndo:', stalker.position)
                    pos_de_recuo = stalker.position.towards(nexus, 3)
                    stalker.move(pos_de_recuo)
                    print('atacando com kite')
                else:
                    print('estou fraco na pos: ', stalker.position)
                    pos_de_recuo = nexus.position.random_on_distance(6)
                    stalker.attack(pos_de_recuo, False)
                    print('recuando com hp:', stalker.health_percentage)
            else:
                stalker.esperando_grupo = True
                if stalker.health_percentage > 0.8 or stalker.shield_health_percentage > 0.5:
                    print('estou prarado para sair com ', stalker.health_percentage, 'de hp e pos:', stalker.position)
                    targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
                    if targets:
                        target = targets.closest_to(stalker)
                        stalker.attack(target)
                    else:
                        stalker.attack(proxy.position.to2.random_on_distance(3))
                else:
                    print('estou fraco na pos: ', stalker.position)
                    pos_de_recuo = nexus.position.random_on_distance(6)
                    stalker.attack(pos_de_recuo, False)
                    print('recuando com hp:', stalker.health_percentage)

        # Build proxy pylon
        if (
            self.structures(UnitTypeId.CYBERNETICSCORE).amount >= 1
            and not self.proxy_built
            and self.can_afford(UnitTypeId.PYLON)
        ):
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 30).random_on_distance(20)
            await self.build(UnitTypeId.PYLON, near=p)
            print('p1', p)
            self.proxy_built = True

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


def main():
    sc2.run_game(
        sc2.maps.get("KingsCoveLE"),
        [Bot(Race.Protoss, KittingStalkers()), Computer(Race.Terran, Difficulty.VeryHard)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
