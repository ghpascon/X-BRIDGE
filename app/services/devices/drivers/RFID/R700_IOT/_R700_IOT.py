import asyncio
import logging

import httpx

from app.schemas.tag import WriteTagValidator
from app.services.events import events

from .on_event import OnEvent
from .reader_helpers import ReaderHelpers
from .write_commands import WriteCommands


class R700_IOT(OnEvent, ReaderHelpers, WriteCommands):
    def __init__(self, config, name):
        self.is_rfid_reader = True

        self.config = config
        self.name = name
        self.urlBase = f'https://{self.config.get("CONNECTION")}/api/v1'
        self.endpoint_interface = f"{self.urlBase}/system/rfid/interface"
        self.endpoint_start = f"{self.urlBase}/profiles/inventory/start"
        self.endpoint_stop = f"{self.urlBase}/profiles/stop"
        self.endpointDataStream = f"{self.urlBase}/data/stream"
        self.endpoint_gpo = f"{self.urlBase}/device/gpos"
        self.endpoint_write = f"{self.urlBase}/profiles/inventory/tag-access"

        self.interface_config = {"rfidInterface": "rest"}
        self.auth = httpx.BasicAuth(
            self.config.get("USERNAME", "root"), self.config.get("PASSWORD", "impinj")
        )

        self.tags_to_write = {}

        self.is_connected = False
        self.is_reading = False
        self._stop_connection = False

    async def disconnect(self):
        """Desconecta o reader de forma segura."""
        logging.info(f"🔌 Disconnecting R700_IOT reader: {self.name}")
        self._stop_connection = True

        if self.is_reading:
            try:
                async with httpx.AsyncClient(auth=self.auth, verify=False, timeout=5.0) as session:
                    await self.stop_inventory(session)
            except Exception as e:
                logging.warning(f"⚠️ Error stopping inventory during disconnect: {e}")

        self.is_connected = False
        self.is_reading = False
        asyncio.create_task(events.on_disconnect(self.name))

    async def connect(self):
        self._stop_connection = False
        while not self._stop_connection:
            async with httpx.AsyncClient(auth=self.auth, verify=False, timeout=10.0) as session:
                if self.is_connected:
                    asyncio.create_task(events.on_disconnect(self.name))

                self.is_connected = False
                self.is_reading = False
                success = await self.configure_interface(session)
                if not success:
                    logging.warning("Failed to configure interface")
                    await asyncio.sleep(1)
                    continue

                success = await self.stop_inventory(session)
                if not success:
                    logging.warning("Failed to stop profiles")
                    await asyncio.sleep(1)
                    continue

                if self.config.get("START_READING") or self.config.get("READING_CONFIG").get(
                    "startTriggers"
                ):
                    success = await self.start_inventory(session)
                    if not success:
                        logging.warning("Failed to start inventory")
                        await asyncio.sleep(1)
                        continue
                if self.config.get("START_READING"):
                    self.is_reading = True

                for i in range(1, 4):
                    asyncio.create_task(self.write_gpo(pin=i, state=False))

                self.is_connected = True
                asyncio.create_task(events.on_connect(self.name))
                await self.get_tag_list(session)

    async def clear_tags(self):
        self.tags = {}

    async def write_gpo(
        self,
        pin: int = 1,
        state: bool | str = True,
        control: str = "static",
        time: int = 1000,
        *args,
        **kwargs,
    ):
        gpo_command = await self.get_gpo_command(pin=pin, state=state, control=control, time=time)
        try:
            async with httpx.AsyncClient(auth=self.auth, verify=False, timeout=10.0) as session:
                await self.post_to_reader(
                    session, self.endpoint_gpo, payload=gpo_command, method="put"
                )
        except Exception as e:
            logging.warning(f"Failed to set GPO: {e}")

    async def write_epc(self, tag_commands):
        """
        Writes a new EPC (Electronic Product Code) to RFID tags.
        """
        if isinstance(tag_commands, dict):
            tag_commands = [tag_commands]

        all_commands = []
        for tag in tag_commands:
            try:
                validated_tag = WriteTagValidator(**tag)
                all_commands.append(await self.get_write_cmd(validated_tag))
            except Exception as e:
                logging.warning(e)
                continue

        await self.send_write_command(all_commands)
