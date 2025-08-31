import json
import os

from app.schemas.logger import logger_manager


class Settings:
    def __init__(self, config_path="config/config.json"):
        """Application settings loader and manager."""
        self.load(config_path)

    def load(self, config_path="config/config.json"):
        """Load configuration from JSON files."""
        self._config_path = config_path
        self.data = {}
        self.data["STORAGE_DAYS"] = 1

        # Load main config
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading {self._config_path}: {e}")

        # Load actions config and override STORAGE_DAYS if present
        actions_path = "config/actions.json"
        if os.path.exists(actions_path):
            try:
                with open(actions_path, "r") as f:
                    actions_data = json.load(f)
                    self.data["STORAGE_DAYS"] = actions_data.get("STORAGE_DAYS", 1)
            except Exception as e:
                print(f"Error loading {actions_path}: {e}")

        logger_manager.load()

    def save(self):
        """Save current configuration to file."""
        with open(self._config_path, "w") as f:
            json.dump(self.data, f, indent=4)


settings = Settings()
