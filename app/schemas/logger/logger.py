import json
import logging
import os
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path


class LoggerManager:
    def __init__(self):
        self.log_dir = None
        self.logs = deque(maxlen=100)

    def load(self):
        # --- Configurações ---
        self.STORAGE_DAYS = 1
        self.LOG_PATH = "Logs"
        if os.path.exists("config/actions.json"):
            with open("config/actions.json", "r") as f:
                actions_data = json.load(f)
                self.STORAGE_DAYS = actions_data.get("STORAGE_DAYS", 1)
                self.LOG_PATH = actions_data.get("LOG_PATH", "Logs")

        # --- Diretório de logs ---
        self.log_dir = Path(self.LOG_PATH)
        self.log_dir.mkdir(exist_ok=True)

        log_filename = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

        # --- Logger principal ---
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Remove handlers antigos
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # --- Handler para arquivo ---
        file_handler = logging.FileHandler(log_filename, mode="a", encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # --- Handler para console ---
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # --- Handler para memória/self.logs ---
        def memory_emit(record):
            log_entry = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s").format(
                record
            )
            self.on_log(log_entry)

        memory_handler = logging.Handler()
        memory_handler.emit = memory_emit
        logger.addHandler(memory_handler)

        logger.info(f"LOG_FILE -> {log_filename}")

    async def clear_old_logs(self):
        cutoff_date = datetime.now() - timedelta(days=self.STORAGE_DAYS)
        for log_path in self.log_dir.glob("*.log"):
            try:
                log_date = datetime.strptime(log_path.stem, "%Y-%m-%d")
                if log_date < cutoff_date:
                    log_path.unlink()
            except ValueError:
                continue  # Ignora arquivos fora do padrão
            except Exception as e:
                logging.error(f"Erro ao remover log {log_path.name}: {e}")

    def on_log(self, message: str):
        """Adiciona o log na memória (deque)"""
        self.logs.appendleft(message)


# --- Instância global ---
logger_manager = LoggerManager()
