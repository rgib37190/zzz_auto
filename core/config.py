from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


@dataclass
class GameConfig:
    resolution: List[int] = field(default_factory=lambda: [1920, 1080])
    language: str = "zh-TW"


@dataclass
class VisionConfig:
    ocr_confidence: float = 0.75
    template_threshold: float = 0.80
    screenshot_interval: float = 0.1


@dataclass
class InputConfig:
    click_delay: float = 0.05
    action_delay: float = 0.2
    loading_timeout: float = 15.0


@dataclass
class DungeonConfig:
    max_stamina_usage: int = 240
    hollow_zero_difficulty: int = 3
    combat_sim_repeat: int = 6


@dataclass
class AppConfig:
    game: GameConfig = field(default_factory=GameConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    input: InputConfig = field(default_factory=InputConfig)
    dungeon: DungeonConfig = field(default_factory=DungeonConfig)

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        config = cls()
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            section_map = {
                "game": (GameConfig, "game"),
                "vision": (VisionConfig, "vision"),
                "input": (InputConfig, "input"),
                "dungeon": (DungeonConfig, "dungeon"),
            }
            for section_key, (cfg_cls, attr_name) in section_map.items():
                if section_key in data:
                    current = vars(getattr(config, attr_name))
                    merged = {**current, **data[section_key]}
                    # Filter out unknown keys
                    valid_keys = {f.name for f in cfg_cls.__dataclass_fields__.values()}
                    filtered = {k: v for k, v in merged.items() if k in valid_keys}
                    setattr(config, attr_name, cfg_cls(**filtered))
        return config
