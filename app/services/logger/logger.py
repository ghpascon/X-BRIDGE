import logging
import sys
import asyncio
import threading
import queue
import os
from collections import deque
from datetime import datetime
from typing import Callable, Optional


class AsyncRotatingHandler(logging.Handler):
    """Asynchronous rotating log handler (custom backup names, non-blocking writes)."""

    def __init__(
        self,
        filename: str,
        max_bytes: int = 10 * 1024 * 1024,
        max_backup_files: int = 3,
    ):
        super().__init__()
        self.filename = filename
        self.max_bytes = max_bytes
        self.max_backup_files = max_backup_files
        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put_nowait(msg + "\n")
        except Exception:
            self.handleError(record)

    def _worker(self):
        while not self.stop_event.is_set():
            try:
                msg = self.log_queue.get(timeout=0.5)
                self._write(msg)
            except queue.Empty:
                continue

    def _write(self, msg: str):
        """Writes a log line and rotates if file exceeds size limit."""
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > self.max_bytes:
            self._rotate_logs()
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(msg)

    def _rotate_logs(self):
        """Rotate the log file and keep only a limited number of backups."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base, _ = os.path.splitext(self.filename)
        backup_name = f"{base}_{timestamp}.log"
        os.rename(self.filename, backup_name)

        # --- Cleanup old backups ---
        log_dir = os.path.dirname(self.filename)
        base_name = os.path.basename(base)
        backups = sorted(
            [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.startswith(base_name + "_")],
            key=os.path.getmtime,
        )
        if len(backups) > self.max_backup_files:
            for old_file in backups[:-self.max_backup_files]:
                try:
                    os.remove(old_file)
                except Exception as e:
                    print(f"Warning: could not remove old log {old_file}: {e}")

    def close(self):
        self.stop_event.set()
        self.thread.join(timeout=2)
        super().close()


class LoggerManager:
    def __init__(self, max_logs: int = 100, memory_callback: Optional[Callable[[str], None]] = None):
        self.logs = deque(maxlen=max_logs)
        self.memory_callback = memory_callback
        self.project_name = os.path.basename(os.getcwd())

    def load(self, log_path: str, max_backup_files: int = 3):
        os.makedirs(log_path, exist_ok=True)
        log_file = os.path.join(log_path, f"{self.project_name}.log")

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Remove old handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Async file handler with max backups
        file_handler = AsyncRotatingHandler(log_file, max_backup_files=max_backup_files)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Memory handler
        memory_handler = logging.Handler()
        memory_handler.emit = self._memory_emit
        logger.addHandler(memory_handler)

        # Exception handling
        sys.excepthook = self.handle_exception
        try:
            loop = asyncio.get_event_loop()
            loop.set_exception_handler(self.asyncio_exception_handler)
        except RuntimeError:
            pass

        logging.info(f"Logger initialized at: {log_file}")

    def _memory_emit(self, record: logging.LogRecord):
        log_entry = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s").format(record)
        self.logs.appendleft(log_entry)
        if self.memory_callback:
            self.memory_callback(log_entry)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def asyncio_exception_handler(self, loop, context):
        exception = context.get("exception")
        if exception:
            logging.error("Unhandled asyncio exception", exc_info=exception)
        else:
            logging.error(f"Unhandled asyncio error: {context.get('message')}")

    def on_log(self, message: str):
        self.logs.appendleft(message)
        if self.memory_callback:
            self.memory_callback(message)

    def get_logs(self, n: int = 50):
        return list(self.logs)[:n]


logger_manager = LoggerManager()
