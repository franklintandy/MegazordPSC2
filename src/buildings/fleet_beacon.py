from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId

import sc2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

class FleetBeacon():
    def __init__(self, bot: sc2.BotAI):
        self.bot = bot

    async def build_fleet_beacon(self):
        if (self.bot.structures(UnitTypeId.PYLON).amount > 0):
            pylon = self.bot.structures(UnitTypeId.PYLON).ready.random
            if self.bot.structures(UnitTypeId.STARGATE).amount > 0:
                # If we have no fleet beacon, build one
                if not self.bot.structures(UnitTypeId.FLEETBEACON):
                    if (
                        self.bot.can_afford(UnitTypeId.FLEETBEACON)
                        and self.bot.already_pending(UnitTypeId.FLEETBEACON) == 0
                    ):
                        await self.bot.build(UnitTypeId.FLEETBEACON, near=pylon)

    # Increases Phoenix weapon range
    def research_pulse_crystals(self):
        if (
            self.bot.structures(UnitTypeId.FLEETBEACON).ready
            and self.bot.can_afford(AbilityId.RESEARCH_PHOENIXANIONPULSECRYSTALS)
            and self.bot.already_pending_upgrade(UpgradeId.ANIONPULSECRYSTALS) == 0
        ):
            fleet = self.bot.structures(UnitTypeId.FLEETBEACON).ready.first
            fleet.research(UpgradeId.ANIONPULSECRYSTALS)

    # Voidray upgrade
    def research_vr_speed(self):
        if (
            self.bot.structures(UnitTypeId.FLEETBEACON).ready
            and self.bot.can_afford(AbilityId.FLEETBEACONRESEARCH_RESEARCHVOIDRAYSPEEDUPGRADE)
            and self.bot.already_pending_upgrade(UpgradeId.VOIDRAYSPEEDUPGRADE) == 0
        ):
            fleet = self.bot.structures(UnitTypeId.FLEETBEACON).ready.first
            fleet.research(UpgradeId.VOIDRAYSPEEDUPGRADE)

    # Tempest upgrade
    def research_tempest_upgrade(self):
        if (
            self.bot.structures(UnitTypeId.FLEETBEACON).ready
            and self.bot.can_afford(AbilityId.FLEETBEACONRESEARCH_TEMPESTRESEARCHGROUNDATTACKUPGRADE)
            and self.bot.already_pending_upgrade(UpgradeId.TEMPESTGROUNDATTACKUPGRADE) == 0
        ):
            fleet = self.bot.structures(UnitTypeId.FLEETBEACON).ready.first
            fleet.research(UpgradeId.TEMPESTGROUNDATTACKUPGRADE)