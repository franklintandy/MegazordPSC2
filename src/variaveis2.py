from sc2.unit import Unit
from sc2.position import Point2
from typing import List

gameState = 0
limiteDeGuerreiros =100
warriorsAttack = 25
tuplesNexusCounted = []
current_towns = 1
limiteTowns = 7
limitePylon = 2 + limiteTowns * 1
limiteWorkers = 78
limiteGateway = 9
limiteGeyser = 16
limitPhotonCannon = limitePylon * 7

forte1: Point2 = ""
forte2: Point2 = ""

#Scout
scout: Unit = ""
pointTargetScout: Point2 = ""
listEnemyTargettargted: List[Unit] = []
hunting = False

#switch States
late_game = -1
porcentagemNexusParaPreparar = 0.5
porcentagemWorkersParaFortificar = 0.7

#states
expandirState = 1
prepararState = 2
fortificarState = 3
manterState = 4
defenderState = 5
atacarState = 6

