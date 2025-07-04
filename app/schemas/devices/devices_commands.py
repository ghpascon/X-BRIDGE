from ..rfid import rfid


class DevicesCommands:
    async def start_inventory(self, device: str | None):
        await self.devices[device].start_inventory()

    async def stop_inventory(self, device: str | None):
        await self.devices[device].stop_inventory()

    async def clear_tags(self, device: str | None = None):
        await rfid.clear_tags(device)

    async def set_gpo(self, device: str, gpo_data : dict):
        if hasattr(self.devices[device], 'set_gpo'):
            await self.devices[device].set_gpo(gpo_data)
            return True
        return False