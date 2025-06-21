import asyncio
from datetime import datetime

from ...db.database import database_engine
from ...models.rfid import DbTag
import logging
from .actions import RFIDAction
from .on_event import OnEvent


class RFID(OnEvent, RFIDAction):
    def __init__(self):
        self.tags = {}
        self.actions = {}
        asyncio.run(self.set_actions(None))

    async def clear_tags(self, device: str | None = None):
        if device is None:
            self.tags = {}
            return
        self.tags = {k: v for k, v in self.tags.items() if v.get("device") != device}
        logging.info(f"[ CLEAR ] -> Reader: {device}")

    async def save_tags(self, device):
        try:
            time = datetime.now()
            async with database_engine.get_db() as db:
                for epc in self.tags:
                    tag = self.tags.get(epc)
                    if not device == tag.get("device"):
                        continue

                    current_tag = DbTag(
                        datetime=time,
                        device=tag.get("device"),
                        epc=tag.get("epc"),
                        tid=tag.get("tid"),
                        ant=tag.get("ant"),
                        rssi=tag.get("rssi"),
                    )

                    if current_tag.epc is None:
                        continue
                    db.add(current_tag)

                await db.commit()
                logging.info(f"[ SAVE TAGS ] -> {device}")

        except Exception as e:
            logging.error(f"Erro ao salvar tags: {e}")


rfid = RFID()
