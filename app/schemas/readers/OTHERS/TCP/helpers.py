import asyncio
import logging

from ....events import events


class Helpers:
    async def monitor_connection(self):
        while self.is_connected:
            await asyncio.sleep(1)
            if self.writer.is_closing():
                self.is_connected = False
                logging.info("[DISCONNECTED] Socket closed.")
                break

    async def receive_data(self):
        buffer = ""
        try:
            while True:
                try:
                    data = await asyncio.wait_for(self.reader.read(1024), timeout=0.1)
                except asyncio.TimeoutError:
                    # Timeout: process what's in the buffer as a command
                    if buffer:
                        await self.on_received_cmd(buffer.strip())
                        buffer = ""
                    continue

                if not data:
                    raise ConnectionError("Connection lost")

                buffer += data.decode(errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    await self.on_received_cmd(line.strip())

        except Exception as e:
            self.is_connected = False
            logging.error(f"[RECEIVE ERROR] {e}")

    async def on_received_cmd(self, data: str):
        await events.on_event(self.device_name, self.event_type, data)
