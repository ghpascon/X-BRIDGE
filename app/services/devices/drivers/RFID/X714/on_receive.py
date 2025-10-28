import asyncio
import logging

from app.services.events import events


class OnReceive:
    async def on_receive(self, data, verbose: bool = False):
        if not isinstance(data, str):
            data = data.decode(errors="ignore")
        data = data.replace("\r", "").replace("\n", "")
        data = data.lower()
        if verbose:
            logging.info(f"{self.name} -> 📥 Received Data: {data}")

        if data.startswith("#read:"):
            self.is_reading = data.endswith("on")
            if self.is_reading:
                await self.clear_tags()
                await self.on_start()
            else:
                await self.on_stop()

        elif data.startswith("#t+@"):
            tag = data[4:]
            epc, tid, ant, rssi = tag.split("|")
            current_tag = {
                "device": self.name,
                "epc": epc,
                "tid": tid,
                "ant": int(ant),
                "rssi": int(rssi) * (-1),
            }
            asyncio.create_task(self.on_tag(current_tag))

        elif len(data) == 24:
            current_tag = {
                "device": self.name,
                "epc": data,
                "tid": None,
                "ant": 1,
                "rssi": 0,
            }
            asyncio.create_task(self.on_tag(current_tag))

        elif data.startswith("#set_cmd:"):
            logging.info(f"CONFIG -> {data[data.index(':')+1:]}")


    async def on_start(self):
        await events.on_start(self.name)

    async def on_stop(self):
        await events.on_stop(self.name)

    async def on_tag(self, tag: dict):
        target = await events.on_tag(tag)
        if target is None:
            return
        asyncio.create_task(self.write_epc({"target_identifier":"tid", "target_value":tag.get("tid"), "new_epc":target, "password":"00000000"}))
        