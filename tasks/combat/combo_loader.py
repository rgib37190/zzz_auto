from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class ComboConfig:
    character: str
    combo_sequence: List[Dict]
    priority_reactions: Dict[str, int] = field(default_factory=dict)


def load_combo(path: Path) -> Optional[ComboConfig]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ComboConfig(
        character=data["character"],
        combo_sequence=data["combo_sequence"],
        priority_reactions=data.get("priority_reactions", {}),
    )


def load_all_combos(directory: Path) -> Dict[str, ComboConfig]:
    combos = {}
    if not directory.exists():
        return combos
    for path in directory.glob("*.yaml"):
        combo = load_combo(path)
        if combo:
            combos[combo.character] = combo
    return combos
