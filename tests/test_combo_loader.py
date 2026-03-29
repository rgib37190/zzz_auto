from pathlib import Path

import yaml

from tasks.combat.combo_loader import ComboConfig, load_combo, load_all_combos


class TestComboLoader:
    def test_load_combo_from_yaml(self, tmp_path):
        combo_file = tmp_path / "ellen.yaml"
        combo_file.write_text(
            yaml.dump(
                {
                    "character": "艾蓮",
                    "combo_sequence": [
                        {"action": "attack", "count": 3, "interval": 0.15},
                        {"action": "skill", "hold": True, "duration": 0.5},
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
        combo = load_combo(combo_file)
        assert combo.character == "艾蓮"
        assert len(combo.combo_sequence) == 2
        assert combo.combo_sequence[0]["action"] == "attack"
        assert combo.combo_sequence[0]["count"] == 3
        assert combo.priority_reactions["dodge_signal"] == 10

    def test_load_all_combos(self, tmp_path):
        for name in ["a.yaml", "b.yaml"]:
            (tmp_path / name).write_text(
                yaml.dump(
                    {
                        "character": name[0],
                        "combo_sequence": [
                            {"action": "attack", "count": 1, "interval": 0.1}
                        ],
                        "priority_reactions": {"dodge_signal": 10},
                    }
                )
            )
        combos = load_all_combos(tmp_path)
        assert len(combos) == 2
        chars = {c.character for c in combos.values()}
        assert "a" in chars
        assert "b" in chars

    def test_load_combo_missing_file(self, tmp_path):
        combo = load_combo(tmp_path / "nope.yaml")
        assert combo is None
