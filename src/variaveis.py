from sc2.unit import Unit
from sc2.position import Point2
from typing import List

gameState = 0
limiteDeGuerreiros =100
warriorsAttack = 25
limiteTowns = 7
limitePylon = 2 + limiteTowns * 1
limiteWorkers = limiteTowns*11
limiteGateway = 9
limiteGeyser = 2 + limiteTowns * 1
limitPhotonCannon = limitePylon * 7

forte1: Point2 = ""
forte2: Point2 = ""

#Scout
scout: Unit = ""
pointTargetScout: Point2 = ""
listEnemyTargettargted: List[Unit] = []
hunting = False

#switch States
porcentagemNexusParaPreparar = 0.6
porcentagemWorkersParaFortificar = 0.6

#states
expandirState = 1
prepararState = 2
fortificarState = 3
manterState = 4
defenderState = 5
atacarState = 6

