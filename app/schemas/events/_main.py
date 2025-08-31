import asyncio
import logging
from collections import deque

from app.db.database import database_engine
from app.models.rfid import DbTag

from .actions import Actions
from .on_event import OnEvent


class Events(OnEvent, Actions):
    def __init__(self):
        self.tags = {}
        self.events = deque(maxlen=20)
        self.actions = {}
        asyncio.run(self.set_actions(None))

    async def clear_tags(self, device: str | None = None):
        if device is None:
            self.tags = {}
            return
        self.tags = {k: v for k, v in self.tags.items() if v.get("device") != device}
        logging.info(f"[ CLEAR ] -> Reader: {device}")

    async def save_tags(self):
        try:
            async with database_engine.get_db() as db:
                for tag in self.tags.values():
                    current_tag = DbTag(**tag)

                    if current_tag.epc is None:
                        continue

                    db.add(current_tag)

                await db.commit()
                logging.info("Tags salvas")

        except Exception as e:
            logging.error(f"Erro ao salvar tags: {e}")


events = Events()
