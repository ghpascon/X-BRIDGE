import logging
from datetime import datetime

from pydantic import ValidationError
from pyepc import SGTIN

from app.schemas.tag import TagSchema


class OnEvent:
    async def on_tag(self, tag: dict, verbose: bool = True):
        """
        Handle a tag read event.

        Args:
            tag (dict): Raw tag data.
            verbose (bool): If True, log/print when a new tag is added.
        """
        try:
            # Validate incoming tag structure
            tag_validado = TagSchema(**tag)

            # Check if tag already exists
            tag_exist = False
            if tag_validado.epc in self.tags:
                self.tags[tag_validado.epc]["timestamp"] = datetime.now()
                tag_exist = True

            # If tag already exists, only update if stronger RSSI
            if tag_exist:
                if tag_validado.rssi is None or self.tags[tag_validado.epc].get("rssi") is not None:
                    return None
                if tag_validado.rssi <= self.tags[tag_validado.epc].get("rssi"):
                    return None

            # Try decoding GTIN from EPC
            try:
                gtin = SGTIN.decode(tag_validado.epc).gtin
            except Exception:
                gtin = ""

            # Build normalized tag object
            current_tag = {
                "timestamp": datetime.now(),
                "device": tag_validado.device,
                "epc": tag_validado.epc,
                "tid": tag_validado.tid,
                "ant": tag_validado.ant,
                "rssi": tag_validado.rssi,
                "gtin": gtin,
            }

            # Save tag
            self.tags[tag_validado.epc] = current_tag

            # Log only when new tag is detected
            if verbose and not tag_exist:
                logging.info(f"[TAG] {current_tag}")

            # Trigger event hook
            await self.on_tag_events(current_tag)

        except ValidationError as e:
            logging.error(f"❌ Invalid tag: {e.json()}")

        return None

    async def on_start(self, device: str) -> None:
        """
        Handle 'start inventory' event for a device.
        """
        logging.info(f"[ START ] -> Reader: {device}")
        await self.clear_tags(device)  # Clear tags for this device
        await self.on_event(device, "inventory", True)

    async def on_stop(self, device: str) -> None:
        """
        Handle 'stop inventory' event for a device.
        """
        logging.info(f"[ STOP ] -> Reader: {device}")
        await self.on_event(device, "inventory", False)
        return len(self.tags)

    async def on_event(self, device: str, event_type: str, event_data) -> None:
        """
        Handle a generic event.

        Args:
            device (str): Reader name.
            event_type (str): Event type (e.g., "tag", "inventory").
            event_data (Any): Event payload.
        """
        if event_type == "tag":
            await self.on_tag(event_data)
            return

        timestamp = datetime.now()
        logging.info(f"[ EVENT ] - {timestamp} - {device} - {event_type} - {event_data}")
        await self.on_events(device, event_type, event_data, timestamp)

    async def on_connect(self, device: str) -> None:
        """Handle reader connection."""
        await self.on_event(device, "connection_event", True)

    async def on_disconnect(self, device: str) -> None:
        """Handle reader disconnection."""
        await self.on_event(device, "connection_event", False)
