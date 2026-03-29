import logging
from unittest.mock import MagicMock

from tasks.base_task import TaskResult, TaskStatus
from tasks.dungeon.combat_simulation import CombatSimulation
from tasks.dungeon.periodic_challenge import PeriodicChallenge
from tasks.dungeon.hollow_zero import HollowZero
from tasks.combat.combo_loader import ComboConfig


def make_combo():
    return ComboConfig(
        character="test",
        combo_sequence=[{"action": "attack", "count": 3, "interval": 0.15}],
        priority_reactions={"dodge_signal": 10},
    )


class TestCombatSimulation:
    def test_name(self):
        task = CombatSimulation(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        assert task.name == "combat_simulation"

    def test_stops_when_no_stamina(self):
        game_state = MagicMock()
        game_state.can_spend_stamina.return_value = False
        task = CombatSimulation(
            MagicMock(), MagicMock(), game_state, logging.getLogger("t"), make_combo()
        )
        result = task.execute()
        assert result.status == TaskStatus.SKIPPED


class TestPeriodicChallenge:
    def test_name(self):
        task = PeriodicChallenge(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        assert task.name == "periodic_challenge"


class TestHollowZero:
    def test_name(self):
        task = HollowZero(
            MagicMock(), MagicMock(), MagicMock(), logging.getLogger("t"), make_combo()
        )
        assert task.name == "hollow_zero"
