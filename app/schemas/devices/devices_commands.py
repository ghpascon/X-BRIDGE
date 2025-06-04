from ..rfid import rfid

class DevicesCommands:
    async def start_inventory(self, reader: str | None):
        await self.devices[reader].start_inventory()

    async def stop_inventory(self, reader: str | None):
        await self.devices[reader].stop_inventory()

    async def clear_tags(self, reader: str | None):
        await rfid.clear_tags(reader)        