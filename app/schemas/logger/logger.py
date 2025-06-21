import logging
from datetime import datetime, timedelta
from pathlib import Path
import os
import json

class LoggerManager:
    def __init__(self):
        self.log_dir = None

    def load(self):
        self.STORAGE_DAYS = 1
        self.LOG_PATH = "Logs"
        if os.path.exists("config/actions.json"):
            with open("config/actions.json", "r") as f:
                actions_data = json.load(f)
                self.STORAGE_DAYS = actions_data.get("STORAGE_DAYS", 1)
                self.LOG_PATH = actions_data.get("LOG_PATH", "Logs")

        self.log_dir = Path(self.LOG_PATH)
        self.log_dir.mkdir(exist_ok=True)

        log_filename = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Remove todos os handlers antigos
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Cria handler para arquivo
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Cria handler para o console
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logger.info(f"LOG_FILE -> {log_filename}")

    async def clear_old_logs(self):
        storage_days = self.STORAGE_DAYS
        cutoff_date = datetime.now() - timedelta(days=storage_days)

        for log_path in self.log_dir.glob("*.log"):
            try:
                log_date = datetime.strptime(log_path.stem, "%Y-%m-%d")
                if log_date < cutoff_date:
                    log_path.unlink()
            except ValueError:
                continue  # Ignora arquivos com nome fora do padrão
            except Exception as e:
                print(f"Erro ao remover log {log_path.name}: {e}")

logger_manager = LoggerManager()
