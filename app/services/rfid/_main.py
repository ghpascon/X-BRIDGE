from .devices import Devices
import logging
from .events import Events


class RfidManager:
	def __init__(self, devices_path: str, example_path: str = ''):
		logging.info(f"{'='*60}")
		logging.info('Initializing RfidManager')

		# Events
		self.events = Events()

		# connect to devices
		self.devices = Devices(devices_path=devices_path, example_path=example_path)

		# set event handlers
		for device in self.devices.devices:
			device.on_event = self.events.on_event
