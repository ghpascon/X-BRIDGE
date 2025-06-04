from ....core.config import settings
from ...rfid import rfid
import asyncio

class OnEvent:
    async def on_start(self):
        print('[ START ]')
        await rfid.clear_tags(self.config.get("NAME"))
        self.is_reading = True

    async def on_stop(self):
        self.is_reading = False
        print('[ STOP ]')

    async def on_tag(self, tag):
        current_tag = {
                "device":self.config.get("NAME"),
                "epc":tag.get('epcHex'),
                "tid":tag.get('tidHex'),
                "ant":tag.get('antennaPort'),
                "rssi":int(tag.get('peakRssiCdbm', 0)/100),
            }
        asyncio.create_task(rfid.on_tag(current_tag))