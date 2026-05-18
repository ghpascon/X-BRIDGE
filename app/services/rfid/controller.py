"""
Docstring for app.services.rfid.controller
This module will be used for custom logic.
"""

from smartx_rfid.devices import DeviceManager
from smartx_rfid.utils import TagList
from smartx_rfid.dispatcher import EventDispatcher
from app.core import DISPATCHER_PATH, EXAMPLES_DISPATCHER_PATH
from .integration import Integration
import asyncio
from app.core import settings
import logging


class Controller:
	def __init__(self, devices: DeviceManager, tags: TagList, integration: Integration):
		self.tags = tags
		self.devices = devices
		self.integration = integration
		self.dispatcher = EventDispatcher(
			dispatches_path=DISPATCHER_PATH,
			example_path=EXAMPLES_DISPATCHER_PATH,
		)

	# [ EVENTS ]
	def on_event(self, name: str, event_type: str, event_data):
		logging.info(f'[ EVENT ] {name} - {event_type}: {event_data}')
		asyncio.create_task(
			self.integration.on_event_integration(
				name=name, event_type=event_type, event_data=event_data
			)
		)
		asyncio.create_task(
			self.dispatcher.add_async(name=name, event_type=event_type, data=event_data)
		)

	# [ Reading Events ]
	def on_start(self, name: str):
		logging.info(f'[ START ] {name}')
		self.tags.remove_tags_by_device(device=name)

	def on_stop(self, name: str):
		logging.info(f'[ STOP ] {name}')

	# [ Tag Events ]
	def on_new_tag(self, name: str, tag: dict):
		logging.info(f'[ TAG ] {name} - {tag}')
		asyncio.create_task(self.integration.on_tag_integration(tag=tag))
		asyncio.create_task(self.dispatcher.add_async(name=name, event_type='tag', data=tag))

	def on_existing_tag(self, name: str, tag: dict):
		if settings.ALWAYS_SEND:
			asyncio.create_task(self.integration.on_tag_integration(tag=tag))
			asyncio.create_task(self.dispatcher.add_async(name=name, event_type='tag', data=tag))
