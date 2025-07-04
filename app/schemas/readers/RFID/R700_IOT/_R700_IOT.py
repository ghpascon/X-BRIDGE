import asyncio
import aiohttp
import logging
from app.schemas.validators.tag import WriteTagValidator

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
        self.auth = aiohttp.BasicAuth("root", "impinj")

        self.tags_to_write = {}

        self.is_connected = False
        self.is_reading = False

    async def connect(self):
        while True:
            async with aiohttp.ClientSession(
                auth=self.auth, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                self.is_connected = False
                self.is_reading = False
                success = await self.configure_interface(session)
                if not success:
                    print("Failed to configure interface")
                    await asyncio.sleep(1)
                    continue

                success = await self.stop_inventory(session)
                if not success:
                    print("Failed to stop profiles")
                    await asyncio.sleep(1)
                    continue

                if self.config.get("START_READING") or self.config.get(
                    "READING_CONFIG"
                ).get("startTriggers"):
                    success = await self.start_inventory(session)
                    if not success:
                        print("Failed to start inventory")
                        await asyncio.sleep(1)
                        continue

                for i in range(1, 4):
                    await self.set_gpo({"gpo_pin":i, "state":True})

                self.is_connected = True
                await self.get_tag_list(session)

    async def clear_tags(self):
        self.tags = {}

    async def set_gpo(self, gpo_data: dict):
        gpo_command = await self.get_gpo_command(gpo_data)
        try:
            async with aiohttp.ClientSession(
                auth=self.auth, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                await self.post_to_reader(
                    session, self.endpoint_gpo, payload=gpo_command, method="put"
                )
        except Exception as e:
            logging.error(f"Failed to set GPO: {e}")

    async def write_epc(self, tag_commands):
        """
        Writes a new EPC (Electronic Product Code) to RFID tags.

        Args:
            tag_commands (list[dict] | dict): A dictionary or a list of dictionaries containing tag information.
                Each dictionary must have the following keys:
                    - target_identifier (str): The identifier type used to locate the tag ("EPC", "TID", None).
                    - target_value (str): The current value of the target identifier to find the tag.
                    - new_epc (str): The new EPC value to be written to the tag.
                    - password (str): The password to access the tag.

        Example:
            tag_commands = [
                {
                    "target_identifier": "EPC",
                    "target_value": "300833B2DDD9014000000001",
                    "new_epc": "300833B2DDD9014000000002",
                    "password": "00000000"
                }
            ]

        Notes:
            If a single dictionary is provided, it will be automatically converted into a list.
        """
        if isinstance(tag_commands, dict):
            tag_commands = [tag_commands]

        all_commands = []
        alerts = []

        for tag in tag_commands:
            try:
                validated_tag = WriteTagValidator(**tag)
            except Exception as e:
                alerts.append(e)
                continue

            all_commands.append(await self.get_write_cmd(validated_tag))
        await self.send_write_command(all_commands)
        await self.clear_tags()
        return alerts
