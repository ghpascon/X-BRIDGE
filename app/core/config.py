import json
import logging
import os

from app.services.logger import logger_manager


class Settings:
    def __init__(self, config_path="config/config.json"):
        """Application settings loader and manager."""
        self.load(config_path)

    def load(self, config_path="config/config.json"):
        """Load configuration from JSON files."""
        self._config_path = config_path
        self.data = {}

        # Load main config
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding="utf8") as f:
                    self.data = json.load(f)
            except Exception as e:
                logging.error(f"Error loading {self._config_path}: {e}")

        actions_path = "config/actions.json"
        if os.path.exists(actions_path):
            try:
                with open(actions_path, "r") as f:
                    self.actions_data = json.load(f)
            except Exception as e:
                logging.error(f"Error loading {actions_path}: {e}")

        logger_manager.load()

    def save(self):
        """Save current configuration to file."""
        try:

            logging.info("Salvando em:", self._config_path)
            with open(self._config_path, "w", encoding="utf8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            logging.error(f"Erro ao salvar config: {e}")


settings = Settings()
