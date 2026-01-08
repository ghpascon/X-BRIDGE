import asyncio

from app.services.events import events


class OnEvent:
    async def on_start(self):
        self.is_reading = True
        await events.on_start(self.name)

    async def on_stop(self):
        self.is_reading = False
        await events.on_stop(self.name)

    async def on_tag(self, tag):
        current_tag = {
            "device": self.name,
            "epc": tag.get("epcHex"),
            "tid": tag.get("tidHex"),
            "ant": tag.get("antennaPort"),
            "rssi": int(tag.get("peakRssiCdbm", 0) / 100),
        }
        target = await events.on_tag(current_tag)
        if target is None:
            return

        asyncio.create_task(
            self.write_epc(
                {
                    "target_identifier": "tid",
                    "target_value": current_tag.get("tid"),
                    "new_epc": target,
                    "password": "00000000",
                }
            )
        )
