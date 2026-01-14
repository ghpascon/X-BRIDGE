from app.services import rfid_manager
import logging


async def connect_on_startup():
	"""Connect to RFID devices on application startup."""
	logging.info('Connecting to RFID devices on startup...')
	await rfid_manager.devices.connect_devices()
