import logging
import sys
import asyncio
from collections import deque
from logging.handlers import RotatingFileHandler
from typing import Callable, Optional


class LoggerManager:
    def __init__(self, log_file: str = "app.log", max_logs: int = 100, memory_callback: Optional[Callable[[str], None]] = None):
        """
        Logger Manager robusto.

        Args:
            log_file: arquivo para logs persistentes
            max_logs: número máximo de logs em memória
            memory_callback: callback opcional para cada log emitido
        """
        self.logs = deque(maxlen=max_logs)
        self.memory_callback = memory_callback
        self.log_file = log_file
        self.load()

    def load(self):
        # --- Logger principal ---
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Remove handlers antigos
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # --- Console handler ---
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # --- File handler (rotativo) ---
        file_handler = RotatingFileHandler(self.log_file, maxBytes=5 * 1024 * 1024, backupCount=5,encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # --- Memory handler ---
        memory_handler = logging.Handler()
        memory_handler.emit = self._memory_emit
        logger.addHandler(memory_handler)

        # --- Captura exceções não tratadas ---
        sys.excepthook = self.handle_exception

        # --- Captura exceções asyncio ---
        try:
            loop = asyncio.get_event_loop()
            loop.set_exception_handler(self.asyncio_exception_handler)
        except RuntimeError:
            # Nenhum loop ativo ainda
            pass

    def _memory_emit(self, record: logging.LogRecord):
        """Captura logs em memória e chama callback se houver"""
        log_entry = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s").format(record)
        self.logs.appendleft(log_entry)
        if self.memory_callback:
            self.memory_callback(log_entry)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Captura exceções não tratadas no código síncrono"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def asyncio_exception_handler(self, loop, context):
        """Captura exceções não tratadas em tasks asyncio"""
        exception = context.get("exception")
        if exception:
            logging.error("Unhandled asyncio exception", exc_info=exception)
        else:
            logging.error(f"Unhandled asyncio error: {context.get('message')}")

    def on_log(self, message: str):
        """Adiciona log manual em memória"""
        self.logs.appendleft(message)
        if self.memory_callback:
            self.memory_callback(message)

    def get_logs(self, n: int = 50):
        """Retorna os últimos n logs em memória"""
        return list(self.logs)[:n]


# --- Instância global ---
logger_manager = LoggerManager()
