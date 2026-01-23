from .devices import Devices
import logging
from .events import Events


class RfidManager:
	def __init__(self, devices_path: str, example_path: str = ''):
		logging.info(f"{'='*60}")
		logging.info('Initializing RfidManager')

		# Events
		logging.info('Setting up Events handler')
		self.events = Events()

		# connect to devices
		logging.info('Setting up Devices')
		self.devices = Devices(devices_path=devices_path, example_path=example_path, event_func = self.events.on_event)

		
		logging.info(f"{'='*20} RfidManager initialized {'='*20}")
