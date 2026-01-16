from app.services import rfid_manager
import logging
import asyncio
from app.core import settings
from datetime import datetime, timedelta

async def connect_on_startup():
	"""Connect to RFID devices on application startup."""
	logging.info('Connecting to RFID devices on startup...')
	await rfid_manager.devices.connect_devices()

async def clear_old_tags():
	while True:
		if settings.CLEAR_OLD_TAGS_INTERVAL is None:
			await asyncio.sleep(60)
		await asyncio.sleep(settings.CLEAR_OLD_TAGS_INTERVAL)  
		if len(rfid_manager.events.tags) == 0:
			continue
		
		timestamp = datetime.now() - timedelta(seconds=settings.CLEAR_OLD_TAGS_INTERVAL)
		logging.info(f"Removing tags before {timestamp}")
		rfid_manager.events.tags.remove_tags_before_timestamp(timestamp)

		