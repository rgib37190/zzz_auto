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
            if "game" in data:
                config.game = GameConfig(**{**vars(config.game), **data["game"]})
            if "vision" in data:
                config.vision = VisionConfig(
                    **{**vars(config.vision), **data["vision"]}
                )
            if "input" in data:
                config.input = InputConfig(**{**vars(config.input), **data["input"]})
            if "dungeon" in data:
                config.dungeon = DungeonConfig(
                    **{**vars(config.dungeon), **data["dungeon"]}
                )
        return config
