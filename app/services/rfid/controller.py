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
from app.services.license import license_manager
from smartx_rfid.schemas.tag import WriteTagValidator
from app.models.renner import Inventory
from smartx_rfid.clients.renner import get_renner_sku


class Controller:
	def __init__(self, devices: DeviceManager, tags: TagList, integration: Integration):
		self.tags = tags
		self.devices = devices
		self.integration = integration
		self.dispatcher = EventDispatcher(
			dispatches_path=DISPATCHER_PATH,
			example_path=EXAMPLES_DISPATCHER_PATH,
		)
		self.write_list: dict = {}

	# [ EVENTS ]
	def on_event(self, name: str, event_type: str, event_data):
		logging.info(f'[ EVENT ] {name} - {event_type}: {event_data}')
		if not license_manager.validate_license():
			return
		# asyncio.create_task(
		# 	self.integration.on_event_integration(
		# 		name=name, event_type=event_type, event_data=event_data
		# 	)
		# )
		# asyncio.create_task(
		# 	self.dispatcher.add_async(name=name, event_type=event_type, data=event_data)
		# )

	# [ Reading Events ]
	def on_start(self, name: str):
		logging.info(f'[ START ] {name}')
		if not license_manager.validate_license():
			return
		if settings.CLEAR_ON_START:
			self.tags.remove_tags_by_device(device=name)

	def on_stop(self, name: str):
		logging.info(f'[ STOP ] {name}')

	# [ Tag Events ]
	def on_new_tag(self, name: str, tag: dict):
		logging.info(f'[ TAG ] {name} - {tag}')
		if not license_manager.validate_license():
			return
		tag['sku'] = get_renner_sku(tag.get('epc'))

		if self.get_sku(tag.get('sku')):
			logging.info(f"Tag {tag.get('sku')} has a valid SKU")
			asyncio.create_task(
				self.devices.write_gpo(
					name,
					settings.GPO_PIN if settings.GPO_PIN else tag.get('ant'),
					True,
					'pulsed',
					settings.GṔO_TIME,
				)
			)
		# asyncio.create_task(self.integration.on_tag_integration(tag=tag))
		# asyncio.create_task(self.dispatcher.add_async(name=name, event_type='tag', data=tag))

	def on_existing_tag(self, name: str, tag: dict):
		asyncio.create_task(self.check_target(tag))
		# if settings.ALWAYS_SEND:
		# 	if not license_manager.validate_license():
		# 		return
		# 	asyncio.create_task(self.integration.on_tag_integration(tag=tag))
		# 	asyncio.create_task(self.dispatcher.add_async(name=name, event_type='tag', data=tag))

	# [ WRITE LIST ]
	def create_write_list_prefix(self, epcs: list, prefix: str):
		self.clear_write_list()
		for epc in epcs:
			target = f'{prefix}{epc[len(prefix):]}'
			current_tag = self.tags.get_by_identifier(epc)
			if current_tag:
				self.add_to_write_list(current_tag, target)
			else:
				logging.error(f'Epc: {epc} not in tags, skipping...')
		return self.write_list

	def add_to_write_list(self, tag: dict, target: str):
		self.write_list[tag.get('tid')] = {
			'target': target.lower(),
			'original_epc': tag.get('epc'),
		}
		tag['target'] = target
		logging.info(f"Added tag {tag.get('tid')} to write list with target {tag.get('target')}")
		self.on_event(name='write_list', event_type='add_to_write_list', event_data=tag)

	def remove_from_write_list(self, tag: dict):
		tid = tag.get('tid')
		if tid in self.write_list:
			logging.info(f'Removed tag {tid} from write list')
			self.on_event(
				name='write_list',
				event_type='remove_from_write_list',
				event_data={**tag, 'original_epc': self.write_list[tid]['original_epc']},
			)
			del self.write_list[tid]
			if not self.write_list:
				logging.info('Write list is now empty')
				self.on_event(name='write_list', event_type='write_list_empty', event_data={})
				return True
		return False

	def clear_write_list(self):
		self.write_list.clear()
		logging.info('Cleared write list')
		self.on_event(name='write_list', event_type='write_list_cleared', event_data={})

	async def check_target(self, tag: dict):
		target = tag.get('target')
		if not target:
			return
		if tag.get('epc') == tag.get('target'):
			logging.info(f"Tag {tag.get('tid')} already has target EPC, removing from write list")
			tag['target'] = None
			self.remove_from_write_list(tag)
			return
		await self.devices.write_epc(
			device_name=tag.get('device'),
			write_tag=WriteTagValidator(
				target_identifier='tid',
				target_value=tag.get('tid'),
				new_epc=tag.get('target'),
				password='00000000',
			),
		)

	# INVENTORY
	def add_inventory(self, data: list | dict):
		try:
			if isinstance(data, dict):
				data = [data]
			if not isinstance(data, list):
				logging.error('Data must be a list or a dictionary')
				return False

			self.integration.db_manager.bulk_insert(Inventory, data)
			return True
		except Exception as e:
			logging.error(f'Error adding inventory: {e}')
			return False

	def get_inventory_table(self, limit: int = 999999, offset: int = 0):
		try:
			return self.integration.db_manager.get_all(Inventory, limit=limit, offset=offset)
		except Exception as e:
			logging.error(f'Error fetching inventory: {e}')
			return []

	def get_sku(self, sku: str):
		try:
			record = self.integration.db_manager.get_by_field(Inventory, 'sku', sku)
			if record:
				return record.to_dict()
			return None
		except Exception as e:
			logging.error(f'Error fetching SKU {sku}: {e}')
			return None

	def get_quantity(self, sku: str):
		sku_record = self.get_sku(sku)
		if sku_record:
			return sku_record.get('quantity', 0)
		return 0

	def update_quantity(self, sku: str, quantity: int):
		try:
			with self.integration.db_manager.get_session() as session:
				record = session.query(Inventory).filter_by(sku=sku).first()
				if record:
					record.quantity = quantity
					return True
			return False
		except Exception as e:
			logging.error(f'Error updating quantity for SKU {sku}: {e}')
			return False

	def delete_sku(self, sku: str):
		try:
			return self.integration.db_manager.delete_by_field(Inventory, 'sku', sku) > 0
		except Exception as e:
			logging.error(f'Error deleting SKU {sku}: {e}')
			return False

	def clear_inventory_table(self):
		try:
			self.integration.db_manager.clear_table(Inventory)
			return True
		except Exception as e:
			logging.error(f'Error clearing inventory: {e}')
			return False
