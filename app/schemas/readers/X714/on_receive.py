import asyncio

import logging

from ...rfid import rfid


class OnReceive:
    async def on_receive(self, data):
        data = data.decode(errors="ignore")
        data = data.replace("\r", "").replace("\n", "")
        data = data.lower()
        print(f"{self.name} -> 📥 Dados recebidos: {data}")

        if data.startswith("#read:"):
            self.is_reading = data.endswith("on")
            if self.is_reading:
                await self.clear_tags()
                await rfid.on_start(self.name)
            else:
                await rfid.on_stop(self.name)

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
            asyncio.create_task(rfid.on_tag(current_tag))

        elif data.startswith("#set_cmd:"):
            logging.info(f"CONFIG -> {data[data.index(':')+1:]}")
