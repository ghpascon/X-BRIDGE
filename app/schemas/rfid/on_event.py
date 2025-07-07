import asyncio

from pydantic import ValidationError

import logging
from ..validators.tag import TagSchema
from datetime import datetime

class OnEvent:
    async def on_tag(self, tag: dict, verbose: bool=True):
        try:
            tag_validado = TagSchema(**tag)

            tag_exist = False
            if tag_validado.epc in self.tags:
                tag_exist = True

            if tag_exist and tag_validado.rssi <= self.tags[tag_validado.epc].get(
                "rssi"
            ):
                return

            current_tag = {
                "timestamp":datetime.now(),
                "device": tag_validado.device,
                "epc": tag_validado.epc,
                "tid": tag_validado.tid,
                "ant": tag_validado.ant,
                "rssi": tag_validado.rssi,
            }
            self.tags[tag_validado.epc] = current_tag
            if verbose and not tag_exist:
                print(f"[TAG] {current_tag}")
                await self.on_tag_events(current_tag)

        except ValidationError as e:
            logging.error(f"❌ Tag inválida: {e.json()}")

    async def on_start(self, device: str) -> None:
        logging.info(f"[ START ] -> Reader: {device}")
        await self.clear_tags(device)
        await self.on_event(device, "inventory", True)

    async def on_stop(self, device: str) -> None:
        logging.info(f"[ STOP ] -> Reader: {device}")
        await self.on_event(device, "inventory", False)

    async def on_event(self, device: str, event_type: str, event_data) -> None: 
        timestamp = datetime.now()
        logging.info(f"[ EVENT ] - {timestamp} - {device} - {event_type} - {event_data}")
        await self.on_events(device, event_type, event_data, timestamp)
