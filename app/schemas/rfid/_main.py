import asyncio

from ...db.database import database_engine
from ...models.rfid import DbTag
import logging
from .actions import RFIDAction
from .on_event import OnEvent

from collections import deque

class RFID(OnEvent, RFIDAction):
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


rfid = RFID()
