import asyncio

from .....core.config import settings
from ....rfid import rfid


class OnEvent:
    async def on_start(self):
        self.is_reading = True
        await rfid.on_start(self.name)

    async def on_stop(self):
        self.is_reading = False
        await rfid.on_stop(self.name)

    async def on_tag(self, tag):
        current_tag = {
            "device": self.name,
            "epc": tag.get("epcHex"),
            "tid": tag.get("tidHex"),
            "ant": tag.get("antennaPort"),
            "rssi": int(tag.get("peakRssiCdbm", 0) / 100),
        }
        asyncio.create_task(rfid.on_tag(current_tag))
