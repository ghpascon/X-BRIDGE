import asyncio
import logging

from app.services.events import events

from .helpers import Helpers


class TCP(Helpers):
    def __init__(self, config, name):
        self.is_rfid_reader = False

        self.config = config
        self.device_name = name

        self.ip = self.config.get("CONNECTION")
        self.port = self.config.get("PORT", 23)
        self.event_type = self.config.get("EVENT_TYPE", "generic_event")

        self.reader = None
        self.writer = None

        self.is_connected = False

    async def connect(self):
        while True:
            try:
                logging.info(f"Connecting: {self.device_name} - {self.ip}:{self.port}")
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.ip, self.port), timeout=3
                )
                self.is_connected = True
                asyncio.create_task(events.on_connect(self.name))
                logging.info(f"✅ [CONNECTED] {self.device_name} - {self.ip}:{self.port}")

                # Start the receive and monitor tasks
                tasks = [
                    asyncio.create_task(self.receive_data()),
                    asyncio.create_task(self.monitor_connection()),
                ]

                # Wait until one of the tasks completes (e.g. disconnection)
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                # Cancel any remaining tasks
                for task in pending:
                    task.cancel()

                self.is_connected = False
                asyncio.create_task(events.on_disconnect(self.name))
                logging.info(f"🔌 [DISCONNECTED] {self.device_name} - Attempting reconnection...")

            except Exception as e:
                self.is_connected = False
                asyncio.create_task(events.on_disconnect(self.name))
                logging.error(
                    f"❌ [CONNECTION ERROR] {self.device_name}: {e} - Retrying in 3 seconds..."
                )

            await asyncio.sleep(3)

    async def write(self, data: str, verbose=True):
        if self.is_connected and self.writer:
            try:
                data = data + "\n"
                self.writer.write(data.encode())
                await self.writer.drain()
                if verbose:
                    logging.info(f"[SENT] {data.strip()}")
            except Exception as e:
                logging.error(f"[SEND ERROR] {e}")
                self.is_connected = False
                asyncio.create_task(events.on_disconnect(self.name))
