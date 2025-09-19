import asyncio
import logging
from collections import deque

from app.db.database import database_engine
from app.models.rfid import DbTag

from .actions import Actions
from .on_event import OnEvent


class Events(OnEvent, Actions):
    def __init__(self):
        """
        Initialize the Events manager.
        """
        self.tags = {}  # Active tags currently detected
        self.events = deque(maxlen=20)  # Store the last 20 events
        self.actions = {}  # Registered actions
        asyncio.run(self.set_actions(None))  # Initialize actions

    async def clear_tags(self, device: str | None = None):
        """
        Clear tags from memory.
        """
        if device is None:
            self.tags = {}
            logging.info("[ CLEAR ] -> All TAGS")
            return

        # Keep only tags not belonging to the specified device
        self.tags = {k: v for k, v in self.tags.items() if v.get("device") != device}
        logging.info(f"[ CLEAR ] -> Reader: {device}")

    async def save_tags(self):
        """
        Save all tags currently in memory into the database.
        """
        try:
            async with database_engine.get_db() as db:
                for tag in self.tags.values():
                    current_tag = DbTag(**tag)

                    # Skip invalid tags
                    if current_tag.epc is None:
                        continue

                    db.add(current_tag)

                await db.commit()
                logging.info("✅ Tags saved to database")

        except Exception as e:
            logging.error(f"❌ Error saving tags: {e}")


events = Events()
