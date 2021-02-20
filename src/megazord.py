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

import variaveis

import zerg_rush



class CannonRushBot(sc2.BotAI):
#################################
    async def found_any_enemy(self, iteration):
        enemyUnits = (self.enemy_units | self.enemy_structures)
        if enemyUnits.amount>0:
                for enemy in enemyUnits:
                    if not enemy in variaveis.listEnemyTargettargted:
                        variaveis.listEnemyTargettargted.append(enemy) 
                        # print("found " +str(enemy.name)+"."+str(enemy.tag)+" -> "+str(len(variaveis.listEnemyTargettargted)))

        if len(variaveis.listEnemyTargettargted)>0:
            for enemy in variaveis.listEnemyTargettargted:
                if self.all_own_units.closer_than(5, enemy.position).amount > 0:
                    if not enemy in enemyUnits:
                        variaveis.listEnemyTargettargted.remove(enemy)
                        # print("remove " +str(enemy.name)+"."+str(enemy.tag)+" -> "+str(len(variaveis.listEnemyTargettargted)))
        return
####################################################################
    def scout_on_step(self, iteration):   
        scout = ""
        if variaveis.scout:
            scout = self.units.find_by_tag(variaveis.scout.tag)
        variaveis.scout = scout

        if not scout:
            if self.workers.amount>0:
                variaveis.scout = self.workers.first
            elif self.units.amount>0:
                variaveis.scout = self.units.random

            if variaveis.scout:
                scout = self.units.find_by_tag(variaveis.scout.tag)
            else:
                return

        if scout:
            if (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_attack).closer_than(15, scout).amount>0:
                variaveis.pointTargetScout = ""

            if not variaveis.pointTargetScout or scout.distance_to(variaveis.pointTargetScout) < 1:
                targets = self.vespene_geyser
                for el in targets:
                    if self.all_own_units.closer_than(9, el).amount > 0 :
                        targets.remove(el)
                if targets.amount>0:
                    variaveis.pointTargetScout = targets.random.position
            
            if variaveis.pointTargetScout:
                if scout.distance_to(variaveis.pointTargetScout) < 5:
                    variaveis.pointTargetScout = ""
                else:
                    scout.scan_move(variaveis.pointTargetScout)
        return
        
#############################################
    async def attack_units(self, iteration, units, limitToAttack):
        # airUnits = units.filter(lambda unit: unit.can_attack_air)
        targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)
        supectsTargets: Units = Units(variaveis.listEnemyTargettargted, self)
        targetsEnemyCanAttack = targets.filter(lambda unit: unit.can_attack)
        targetToMove = ""
        if supectsTargets:            
            targetToMove = supectsTargets.closest_to(self.enemy_start_locations[0]).position   

        for warrior in units:         
            enemyCloserThan20 = targets.closer_than(25,warrior)
            unitsCloserThan10 = units.closer_than(int(variaveis.warriorsAttack*0.7), warrior)
        #Abilitys
            if targetsEnemyCanAttack.closer_than(10, warrior):
                # print(warrior.name)                
                if warrior.type_id == UnitTypeId.SENTRY:
                    warrior(AbilityId.FORCEFIELD_FORCEFIELD, targetsEnemyCanAttack.closest_to(warrior).position)
                    warrior(AbilityId.GUARDIANSHIELD_GUARDIANSHIELD)
                if warrior.type_id == UnitTypeId.STALKER:
                    warrior(AbilityId.EFFECT_BLINK_STALKER, targetsEnemyCanAttack.closest_to(warrior).position)
                if warrior.type_id == UnitTypeId.VOIDRAY:
                    warrior(AbilityId.EFFECT_VOIDRAYPRISMATICALIGNMENT)
        #decisão de alvo
            if targets:                
                if enemyCloserThan20.closer_than(8,warrior).amount > 0:
                    warrior.attack(targets.closest_to(warrior))
                elif enemyCloserThan20.amount==0 and targets.closer_than(5,warrior):
                     warrior.attack(self.enemy_structures.closest_to(warrior))
                elif enemyCloserThan20.amount*0.5 <= unitsCloserThan10.amount:
                    warrior.attack(targets.closest_to(warrior))
                    # print("tem gente atacando")
                elif enemyCloserThan20.amount*0.5 > unitsCloserThan10.amount:
                    furthesWarrior = units.furthest_to(targets.closest_to(warrior))
                    warrior.move(furthesWarrior)           
                elif enemyCloserThan20.amount == 0:
                    warriorsClosestEnenmy = units.closest_to(targets.closest_to(warrior))
                    warrior.move(warriorsClosestEnenmy)
            # elif self.enemy_units.closer_than(15,warrior).amount > 0:
            #     warrior.attack(self.enemy_units.closest_to(warrior))
            # elif targets.closer_than(15,warrior).amount > 0:
            #     warrior.attack(targets.closest_to(warrior))
            elif units.amount >= limitToAttack and unitsCloserThan10.amount>=limitToAttack*0.5:  
                if targets:
                    if unitsCloserThan10.amount>=targets.closer_than(10, warrior).amount*0.6:
                        warrior.attack(targets.closest_to(warrior))
                    else:
                        furthesWarrior = units.furthest_to(targetsEnemyCanAttack.closest_to(warrior))
                        warrior.move(furthesWarrior)
                elif variaveis.hunting and targetToMove:
                    # print("Scann")
                    warrior.scan_move(targetToMove)
                else:
                    warrior.attack(self.enemy_start_locations[0])
                    if warrior.distance_to(self.enemy_start_locations[0])<5:
                        variaveis.hunting = True
            else:                                
                targetsHome = (self.townhalls | self.structures(UnitTypeId.PYLON))
                targettoMove = self.start_location
                # if self.structures(UnitTypeId.PYLON).amount>0:
                #     targettoMove = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations)                    
                if targetsHome:
                    targettoMove = targetsHome.closest_to(self.enemy_start_locations[0])
                    if targets:
                        target = targets.closest_to(warrior)
                        targettoMove = targetsHome.closest_to(target) 
                    
                    warrior.move(targettoMove)
                else:
                    warrior.attack(self.enemy_start_locations[0])

        return

#######################################
    async def military_on_step(self, iteration):         
            if self.workers.amount >= variaveis.limiteWorkers*0.95:
                CannonRushBot.scout_on_step(self, iteration)
        #WARRIORS

            
         #train

            for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                if self.can_afford(UnitTypeId.VOIDRAY):
                    sg.train(UnitTypeId.VOIDRAY)

            for gate in self.structures(UnitTypeId.GATEWAY).ready.idle: 
                if self.units(UnitTypeId.SENTRY).amount <= variaveis.limiteDeGuerreiros:
                    if self.can_afford(UnitTypeId.SENTRY):
                        gate.train(UnitTypeId.SENTRY)
                        if variaveis.warriorsAttack < 40:   
                            variaveis.warriorsAttack = variaveis.warriorsAttack + 0.1

                if self.units(UnitTypeId.STALKER).amount < variaveis.limiteDeGuerreiros:
                    for gate in self.structures(UnitTypeId.GATEWAY).ready.idle:
                        if self.can_afford(UnitTypeId.STALKER):
                            gate.train(UnitTypeId.STALKER)
                            if variaveis.warriorsAttack < 40:  
                                variaveis.warriorsAttack = variaveis.warriorsAttack + 0.1
        
                if self.units(UnitTypeId.ZEALOT).amount < variaveis.limiteDeGuerreiros:
                    for gate in self.structures(UnitTypeId.GATEWAY).ready.idle:
                        if self.can_afford(UnitTypeId.ZEALOT):
                            gate.train(UnitTypeId.ZEALOT)
                            if variaveis.warriorsAttack < 40:  
                                variaveis.warriorsAttack = variaveis.warriorsAttack + 0.1

        #atack

            await CannonRushBot.attack_units(self, iteration, (self.units(UnitTypeId.VOIDRAY) | self.units(UnitTypeId.SENTRY) | self.units(UnitTypeId.ZEALOT) | self.units(UnitTypeId.STALKER)), variaveis.warriorsAttack)
           

            
                

        #STRUCTURE
            if self.structures(UnitTypeId.FORGE).amount + self.already_pending(UnitTypeId.FORGE) < 2:
                pylon_ready = self.structures(UnitTypeId.PYLON).ready
                if pylon_ready.amount > 0:
                    if self.can_afford(UnitTypeId.FORGE):
                        await self.build(UnitTypeId.FORGE, near=pylon_ready.closer_than(20, self.start_location).random)     
            if self.structures(UnitTypeId.FORGE).ready:
                if self.structures(UnitTypeId.GATEWAY).ready:
                    # If we have gateway completed, build cyber core
                    if not self.structures(UnitTypeId.CYBERNETICSCORE):
                        if (
                            self.can_afford(UnitTypeId.CYBERNETICSCORE)
                            and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                        ):
                            pylon = self.structures(UnitTypeId.PYLON).random
                            await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
                # If we have no gateway, build gateway
                if self.can_afford(UnitTypeId.GATEWAY) and self.structures(UnitTypeId.GATEWAY).amount <= variaveis.limiteGateway:                     
                    pylon = self.structures(UnitTypeId.PYLON).random
                    await self.build(UnitTypeId.GATEWAY, near=pylon, placement_step=5) 
        
                if self.structures(UnitTypeId.PHOTONCANNON).amount  + self.already_pending(UnitTypeId.PHOTONCANNON) < variaveis.limitPhotonCannon:
                    if self.structures(UnitTypeId.PYLON).ready.amount >0 :
                        pylon = self.structures(UnitTypeId.PYLON).random               
                        CannonsCloser = self.structures(UnitTypeId.PHOTONCANNON).closer_than(10, pylon)  
                        if CannonsCloser.amount < 5 and self.can_afford(UnitTypeId.PHOTONCANNON):
                            await self.build(UnitTypeId.PHOTONCANNON, near=pylon, placement_step=10)
                if self.structures(UnitTypeId.TWILIGHTCOUNCIL).amount + self.already_pending(UnitTypeId.TWILIGHTCOUNCIL) < 1:
                    pylon_ready = self.structures(UnitTypeId.PYLON).ready
                    if pylon_ready.amount > 0:
                        if self.can_afford(UnitTypeId.TWILIGHTCOUNCIL):
                            await self.build(UnitTypeId.TWILIGHTCOUNCIL, near=pylon_ready.closest_to(self.start_location)) 

                if self.structures(UnitTypeId.STARGATE).amount + self.already_pending(UnitTypeId.STARGATE) < 3:
                    pylon = self.structures(UnitTypeId.PYLON).ready.random
                    if pylon:
                        if self.can_afford(UnitTypeId.STARGATE):
                            await self.build(UnitTypeId.STARGATE, near=pylon)

            return

###############################################
    async def defender_base(self, iteration, units: Units):
        for nexus in self.townhalls:
            enemysNear = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked and unit.is_attacking).closer_than(15, nexus)
            if enemysNear.amount>0:
                ownUnitsNear =  units.filter(lambda unit: unit.can_attack).closer_than(20, nexus)
                print("atacando para defender")
                if ownUnitsNear.amount >= enemysNear.amount*0.6:
                    print("atacando para defender")
                    for unit in ownUnitsNear:
                        unit.attack(enemysNear.closest_to(unit))
                else:
                    print("Foge para defender")
                    nexusAux = self.townhalls
                    nexusAux.remove(nexus)
                    for unit in ownUnitsNear:
                        unit.move(nexusAux.closest_to(nexus))

##########################################
    async def preparing_state(self, iteration, nexus):
        
        if self.structures(UnitTypeId.FORGE).amount + self.already_pending(UnitTypeId.FORGE) < 1:
            pylon_ready = self.structures(UnitTypeId.PYLON).closer_than(40, self.start_location).ready
            if pylon_ready.amount > 0:
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(UnitTypeId.FORGE, near=pylon_ready.closer_than(20, self.start_location).random)                    
        elif self.structures(UnitTypeId.FORGE).ready:
            forge = self.structures(UnitTypeId.FORGE).random
            if self.structures(UnitTypeId.PYLON).closer_than(7, forge).amount<1:                
                    await self.build(UnitTypeId.PYLON, near=forge)
                       #build pylon 
        if self.structures(UnitTypeId.PYLON).closer_than(10, nexus).amount < 1:
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, near=nexus, placement_step=6)
        
        if self.structures(UnitTypeId.PHOTONCANNON).amount  + self.already_pending(UnitTypeId.PHOTONCANNON) < 5:
                if self.structures(UnitTypeId.PYLON).ready.amount >0 :
                    pylon = self.structures(UnitTypeId.PYLON).random               
                    CannonsCloser = self.structures(UnitTypeId.PHOTONCANNON).closer_than(3, pylon)  
                    if CannonsCloser.amount < 5 and self.can_afford(UnitTypeId.PHOTONCANNON):
                        await self.build(UnitTypeId.PHOTONCANNON, near=pylon, placement_step=10)

        if nexus.is_ready and self.structures(UnitTypeId.ASSIMILATOR).amount + self.already_pending(UnitTypeId.ASSIMILATOR)  <= 1:
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break

                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break

                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                        await self.build(UnitTypeId.ASSIMILATOR, vg)
        if self.structures(UnitTypeId.FORGE).ready:                
            if self.can_afford(UnitTypeId.GATEWAY) and self.structures(UnitTypeId.GATEWAY).amount <= 2:                     
                pylon = self.structures(UnitTypeId.PYLON).random
                await self.build(UnitTypeId.GATEWAY, near=pylon, placement_step=5) 
        # Build gas near completed nexuses once we have a cybercore (does not need to be completed  
        # reforçar com cannons   
        
                    
        return

##########################################

    async def reforce(self, iteration, point, pylonCount, limiteCannonPorPylon = 5):
        nearPylons = (self.structures(UnitTypeId.PYLON).closer_than(20, point))
        if nearPylons.amount + self.already_pending(UnitTypeId.PYLON) < pylonCount:
            if self.can_afford(UnitTypeId.PYLON):
                    # print('Building pylon {}'.format(len(self.structures(UnitTypeId.PYLON)) + self.already_pending(UnitTypeId.PYLON)))
                    await self.build(UnitTypeId.PYLON, near=point, placement_step=5)
        if self.structures(UnitTypeId.FORGE).amount + self.already_pending(UnitTypeId.FORGE) < 1:
            pylon_ready = self.structures(UnitTypeId.PYLON).closer_than(15, self.start_location).ready
            if pylon_ready.amount > 0:
                if self.can_afford(UnitTypeId.FORGE):
                    await self.build(UnitTypeId.FORGE, near=pylon_ready.closer_than(20, self.start_location).random)
            else:
                if self.can_afford(UnitTypeId.PYLON) and  self.structures(UnitTypeId.PYLON).amount + self.already_pending(UnitTypeId.PYLON)<2:
                    # print('Building pylon {}'.format(len(self.structures(UnitTypeId.PYLON)) + self.already_pending(UnitTypeId.PYLON)))
                    await self.build(UnitTypeId.PYLON, near=self.start_location, placement_step=7)
        if nearPylons.amount >0:
            if self.can_afford(UnitTypeId.PHOTONCANNON) and self.structures(UnitTypeId.PHOTONCANNON).closer_than(25, point).amount  + self.already_pending(UnitTypeId.PHOTONCANNON) < pylonCount*limiteCannonPorPylon:
                    # print('Building pylon {}'.format(len(self.structures(UnitTypeId.PYLON)) + self.already_pending(UnitTypeId.PYLON)))
                    await self.build(UnitTypeId.PHOTONCANNON, near=point, placement_step=3)

        
        return
################################################


    async def manter_state(self, iteration):
        if not variaveis.forte2:
            variaveis.forte2 = (self.start_location + self.enemy_start_locations[0])/2
        await CannonRushBot.reforce(self, iteration, variaveis.forte2, 2, 6)
        return

##########################################

    async def Status_machine(self, iteration): 
        if iteration == 0 or (self.workers.amount/20 < self.townhalls.amount and self.idle_worker_count>6):
            if variaveis.gameState != variaveis.expandirState:
                await self.chat_send("gameState(expandirState)")
            variaveis.gameState = variaveis.expandirState
        elif self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) >= variaveis.limiteTowns*variaveis.porcentagemNexusParaPreparar and variaveis.gameState <= variaveis.expandirState:
                    variaveis.warriorsAttack = 5
                    variaveis.gameState = variaveis.prepararState
                    await self.chat_send("gameState(prepararState)")
        elif variaveis.gameState <= variaveis.prepararState:
            if self.workers.amount >= variaveis.limiteWorkers*variaveis.porcentagemWorkersParaFortificar:
                    # variaveis.warriorsAttack = 20
                    variaveis.gameState = variaveis.fortificarState
                    await self.chat_send("gameState(fortificarStateState)")
        elif self.supply_army + self.supply_workers >= 190 and variaveis.gameState <= variaveis.fortificarState:
                variaveis.gameState = variaveis.manterState
                await self.chat_send("gameState(manterState)")

        # print("total = " + str(self.supply_army + self.supply_workers))










#On_STEP
###################################







    async def on_step(self, iteration):
        await CannonRushBot.Status_machine(self, iteration)
        
        await CannonRushBot.defender_base(self, iteration, self.units)
        if self.idle_worker_count:
            await self.distribute_workers()
        if iteration == 0:
            self.already_assigned = 0
            await self.chat_send("(expandir)(preparar)(atacar)(gg)")
            # self._find_expansion_locations()

        if not self.townhalls.ready:
            if self.can_afford(UnitTypeId.NEXUS) and self.workers.amount>=1:
                await self.expand_now()
            elif not self.townhalls:
                for worker in self.workers:
                    worker.attack(self.enemy_start_locations[0])
        else:            
            nexus = self.townhalls.random            
            
        
        await CannonRushBot.found_any_enemy(self, iteration)
        
            

        # If this random nexus is not idle and has not chrono buff, chrono it with one of the nexuses we have
        if self.townhalls.amount > 0:
            if not nexus.is_idle:
                nexuses = self.structures(UnitTypeId.NEXUS)
                abilities = await self.get_available_abilities(nexuses)
                for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                        loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                        break
#workers            

        #train Probe
        for nexus in self.townhalls:          
            if variaveis.gameState >= variaveis.expandirState:
                if nexus.is_idle and self.workers.amount <= variaveis.limiteWorkers :
                    if self.can_afford(UnitTypeId.PROBE):
                        nexus.train(UnitTypeId.PROBE)

#STRUCTURES
        #expand Nexus
        if variaveis.gameState >= variaveis.expandirState: 
            if self.townhalls.amount > 0:
                nearPoint = ((self.townhalls.closest_to(self.enemy_start_locations[0]).position * 5) + self.enemy_start_locations[0])/6
                if not variaveis.forte1:
                    variaveis.forte1 = nearPoint
                if self.townhalls.amount>1:
                    await CannonRushBot.reforce(self, iteration, nearPoint, 1, 4) 
                if self.townhalls.ready.amount + self.already_pending(UnitTypeId.NEXUS) <= variaveis.limiteTowns:        
                    if self.can_afford(UnitTypeId.NEXUS):
                        await self.expand_now()
        elif self.can_afford(UnitTypeId.NEXUS):
                await self.expand_now()

        #build pylon 
        if variaveis.gameState >= variaveis.fortificarState: 
            if nexus:
                PylonCloser = self.structures(UnitTypeId.PYLON).closer_than(7, nexus) 
                if PylonCloser.amount < 2 and self.structures(UnitTypeId.PYLON).amount  + self.already_pending(UnitTypeId.PYLON) <= variaveis.limitePylon:
                    if self.can_afford(UnitTypeId.PYLON):
                        # print('Building pylon {}'.format(len(self.structures(UnitTypeId.PYLON)) + self.already_pending(UnitTypeId.PYLON)))
                        await self.build(UnitTypeId.PYLON, near=nexus, placement_step=7)

        # #build vespene_geyser
        if variaveis.gameState >= variaveis.fortificarState:
            if nexus.is_ready and self.structures(UnitTypeId.ASSIMILATOR).amount <= variaveis.limiteGeyser:
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break

                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break

                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                        await self.build(UnitTypeId.ASSIMILATOR, vg)




         # Build gas near completed nexuses once we have a cybercore (does not need to be completed       
        if variaveis.gameState >= variaveis.prepararState:
            await CannonRushBot.preparing_state(self, iteration, nexus)

        
        
        if variaveis.gameState >= variaveis.fortificarState:
            await CannonRushBot.military_on_step(self, iteration)

        
        if variaveis.gameState >= variaveis.manterState:
            await CannonRushBot.manter_state(self,iteration)
            
     
        # if self.workers.amount > variaveis.limiteWorkers:
        #     count = self.workers.amount - variaveis.limiteWorkers
        #     for worker in self.workers:
        #         if count > 0:                    
        #             targets = (self.enemy_units | self.enemy_structures).filter(lambda unit: unit.can_be_attacked)        
        #             if targets.closer_than(10,worker).amount > 0:
        #                 worker.attack(targets.closest_to(worker))
        #             count = count-1

       
#atualizações
        if variaveis.gameState >= variaveis.prepararState:
            await CannonRushBot.research(self,iteration)
        
        #fim
        if not self.townhalls and not self.workers:
            return



#####################################################################
    async def research(self, iteration):
        for forge in self.structures(UnitTypeId.FORGE):
            if forge.is_idle and forge.is_ready:
            #Research Forge1
                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDWEAPONS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1) == 0
                ):
                    forge.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1)
                    
                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSSHIELDS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSSHIELDSLEVEL1) == 0
                ):
                    forge.research(UpgradeId.PROTOSSSHIELDSLEVEL1)

                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDARMOR)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDARMORSLEVEL1) == 0
                ):
                    forge.research(UpgradeId.PROTOSSGROUNDARMORSLEVEL1)
            #Research Forge2
                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDWEAPONS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2) == 0
                ):
                    forge.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2)
                    
                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSSHIELDS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSSHIELDSLEVEL2) == 0
                ):
                    forge.research(UpgradeId.PROTOSSSHIELDSLEVEL2)

                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDARMOR)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDARMORSLEVEL2) == 0
                ):
                    forge.research(UpgradeId.PROTOSSGROUNDARMORSLEVEL2)
            #Research Forge3
                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDWEAPONS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3) == 0
                ):
                    forge.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3)
                    
                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSSHIELDS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSSHIELDSLEVEL3) == 0
                ):
                    forge.research(UpgradeId.PROTOSSSHIELDSLEVEL3)

                if ( 
                    forge.is_ready
                    and forge.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSGROUNDARMOR)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSGROUNDARMORSLEVEL3) == 0
                ):
                    forge.research(UpgradeId.PROTOSSGROUNDARMORSLEVEL3)

        for core in self.structures(UnitTypeId.CYBERNETICSCORE):
            if core.is_idle and core.is_ready:
                
        #research core lvl 1
                if ( 
                    core.is_ready
                    and core.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSAIRARMOR)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL1) == 0
                ):
                    core.research(UpgradeId.PROTOSSAIRARMORSLEVEL1)
                
                if ( 
                    core.is_ready
                    and core.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSAIRWEAPONS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL1) == 0
                ):
                    core.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL1)

                if ( 
                    core.is_ready
                    and core.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSAIRARMOR)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL2) == 0
                ):
                    core.research(UpgradeId.PROTOSSAIRARMORSLEVEL2)
                
                if ( 
                    core.is_ready
                    and core.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSAIRWEAPONS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL2) == 0
                ):
                    core.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL2)
                            
        #research core lvl 3
                if ( 
                    core.is_ready
                    and core.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSAIRARMOR)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL3) == 0
                ):
                    core.research(UpgradeId.PROTOSSAIRARMORSLEVEL3)
                
                if ( 
                    core.is_ready
                    and core.is_idle
                    and self.can_afford(AbilityId.RESEARCH_PROTOSSAIRWEAPONS)
                    and self.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL3) == 0
                ):
                    core.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL3)
                    
#################################################


def main():
    sc2.run_game(
        sc2.maps.get("(2)CatalystLE"),
        [Bot(Race.Protoss, CannonRushBot(), name="Megazord"), Computer(Race.Zerg, Difficulty.VeryHard)],
        # [Bot(Race.Protoss, CannonRushBot(), name="Megazord") , Bot(Race.Zerg, zerg_rush.ZergRushBot(), name="zergRush")],
        realtime=False,
        save_replay_as="Megazord_vs_Protoss_VeryHard.SC2Replay"
    )


if __name__ == "__main__":
    main()
