from pathlib import Path

from core.config import AppConfig


class TestAppConfig:
    def test_load_from_yaml(self, config_dir):
        config = AppConfig.load(config_dir / "settings.yaml")
        assert config.game.resolution == [1920, 1080]
        assert config.game.language == "zh-TW"
        assert config.vision.ocr_confidence == 0.75
        assert config.vision.template_threshold == 0.80
        assert config.input.click_delay == 0.05
        assert config.dungeon.max_stamina_usage == 240

    def test_load_missing_file_uses_defaults(self, tmp_path):
        config = AppConfig.load(tmp_path / "nonexistent.yaml")
        assert config.game.resolution == [1920, 1080]
        assert config.vision.ocr_confidence == 0.75

    def test_partial_override(self, tmp_path):
        partial = tmp_path / "partial.yaml"
        partial.write_text("game:\n  language: zh-CN\n")
        config = AppConfig.load(partial)
        assert config.game.language == "zh-CN"
        assert config.game.resolution == [1920, 1080]  # default preserved
