import os
import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def sample_settings():
    return {
        "game": {"resolution": [1920, 1080], "language": "zh-TW"},
        "vision": {
            "ocr_confidence": 0.75,
            "template_threshold": 0.80,
            "screenshot_interval": 0.1,
        },
        "input": {"click_delay": 0.05, "action_delay": 0.2, "loading_timeout": 15},
        "dungeon": {
            "max_stamina_usage": 240,
            "hollow_zero_difficulty": 3,
            "combat_sim_repeat": 6,
        },
    }


@pytest.fixture
def config_dir(sample_settings, tmp_path):
    config_path = tmp_path / "config"
    config_path.mkdir()
    settings_file = config_path / "settings.yaml"
    settings_file.write_text(yaml.dump(sample_settings))
    combos_dir = config_path / "combos"
    combos_dir.mkdir()
    combo_file = combos_dir / "default.yaml"
    combo_file.write_text(
        yaml.dump(
            {
                "character": "default",
                "combo_sequence": [
                    {"action": "attack", "count": 3, "interval": 0.15}
                ],
                "priority_reactions": {
                    "dodge_signal": 10,
                    "qte_prompt": 9,
                    "ultimate_ready": 8,
                    "switch_prompt": 7,
                },
            }
        )
    )
    return config_path
