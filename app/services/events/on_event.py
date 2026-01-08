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
            if tag_validado.epc in self.tags:
                # APPROACH 1: Tag already exists - Handle updates
                await self._handle_existing_tag(tag_validado, verbose)
            else:
                # APPROACH 2: New tag detected - Handle first detection
                await self._handle_new_tag(tag_validado, verbose)

        except ValidationError as e:
            logging.error(f"❌ Invalid tag: {e.json()}")

        return None

    async def _handle_existing_tag(self, tag_validado: TagSchema, verbose: bool = True):
        """
        Handle updates for an existing tag.

        Args:
            tag_validado (TagSchema): Validated tag data.
            verbose (bool): If True, log updates.
        """
        existing_tag = self.tags[tag_validado.epc]

        # Update timestamp for any detection
        existing_tag["timestamp"] = datetime.now()

        # Update RSSI only if new value is stronger (closer to 0)
        if tag_validado.rssi is not None:
            current_rssi = existing_tag.get("rssi")
            if current_rssi is None or abs(tag_validado.rssi) < abs(current_rssi):
                existing_tag["rssi"] = tag_validado.rssi
                existing_tag["ant"] = tag_validado.ant  # Update antenna too

        # Increment count for existing tag
        existing_tag["count"] = existing_tag.get("count", 1) + 1

    async def _handle_new_tag(self, tag_validado: TagSchema, verbose: bool = True):
        """
        Handle first detection of a new tag.

        Args:
            tag_validado (TagSchema): Validated tag data.
            verbose (bool): If True, log new tag detection.
        """
        # Try decoding GTIN from EPC
        try:
            gtin = SGTIN.decode(tag_validado.epc).gtin
        except Exception:
            gtin = ""

        # Build normalized tag object for new tag
        current_tag = {
            "timestamp": datetime.now(),
            "device": tag_validado.device,
            "epc": tag_validado.epc,
            "tid": tag_validado.tid,
            "ant": tag_validado.ant,
            "rssi": tag_validado.rssi,
            "gtin": gtin,
            "count": 1,
        }

        # Save new tag
        self.tags[tag_validado.epc] = current_tag

        # Log new tag detection
        if verbose:
            logging.info(f"[TAG] {current_tag}")

        # Trigger event hook for new tag
        await self.on_tag_events(current_tag)

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
