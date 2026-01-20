import logging
import os
import json
from smartx_rfid.devices import SERIAL, TCP, R700_IOT, X714
import asyncio
from typing import List, Dict, Optional, Tuple
from smartx_rfid.schemas.tag import WriteTagValidator

class Devices:
	def __init__(self, devices_path: str, example_path: str = ''):
		self.devices = []
		self._devices_path = devices_path
		self._example_path = example_path
		self.load_devices()

	def __len__(self):
		return len(self.devices)

	def load_devices(self):
		logging.info(f'Loading devices from: {self._devices_path}')
		self.devices = []

		try:
			# Create directory if it does not exist
			if not os.path.exists(self._devices_path):
				os.makedirs(self._devices_path)
				logging.info(f'📁 Directory created: {self._devices_path}')
		except Exception as e:
			logging.error(f"❌ Error checking/creating directory '{self._devices_path}': {e}")
			return

		# Iterate over JSON files in the directory
		for filename in os.listdir(self._devices_path):
			if filename.endswith('.json'):
				filepath = os.path.join(self._devices_path, filename)
				logging.info(f'📄 File: {filename}')
				try:
					with open(filepath, 'r', encoding='utf-8') as f:
						data = json.load(f)
					# If the device config is invalid, remove the file
					if data.get('READER') is None:
						os.remove(filepath)
						continue
					name = filename.replace('.json', '')
					device_type = data.get('READER', 'UNKNOWN')
					self.add_device(name, device_type, data)
				except json.JSONDecodeError as e:
					logging.error(f'❌ JSON decode error: {e}')
				except Exception as e:
					logging.error(f"❌ Error processing file '{filename}': {e}")

	def add_device(self, name, device_type, data):
		logging.info(f'🔍 Adding device: {name}')
		logging.info(f'📡 Reader type: {device_type}')

		### SERIAL
		if device_type == 'SERIAL':
			self.devices.append(
				SERIAL(
					name=name,
					port=data.get('PORT', 'AUTO'),
					vid=data.get('VID', 1),
					pid=data.get('PID', 1),
					baudrate=data.get('BAUDRATE', 115200),
				)
			)

		### TCP
		elif device_type == 'TCP':
			self.devices.append(TCP(name=name, ip=data.get('IP'), port=data.get('PORT', 23)))

		### X714
		elif device_type == 'X714':
			self.devices.append(
				X714(
					name=name,
					connection_type=data.get('CONNECTION_TYPE', 'SERIAL'),
					port=data.get('PORT', 'AUTO'),
					baudrate=data.get('BAUDRATE', 115200),
					vid=data.get('VID', 1),
					pid=data.get('PID', 1),
					ip=data.get('IP', '192.168.1.101'),
					tcp_port=data.get('TCP_PORT', 23),
					ble_name=data.get('BLE_NAME', 'SMTX'),
					buzzer=data.get('BUZZER', True),
					session=data.get('SESSION', 1),
					start_reading=data.get('START_READING', False),
					gpi_start=data.get('GPI_START', False),
					ant_dict=data.get('ANT_DICT', None),
				)
			)

		### R700
		elif device_type == 'R700_IOT':
			self.devices.append(
				R700_IOT(
					name=name,
					ip=data.get('IP'),
					username=data.get('USERNAME', 'root'),
					password=data.get('PASSWORD', 'impinj'),
					start_reading=data.get('START_READING', True),
					reading_config=data.get('READING_CONFIG', {}),
				)
			)

		###
		else:
			logging.warning(
				f"⚠️ Unknown reader type '{device_type}'. Device '{name}' was not added."
			)
			return  # Exit early if device is invalid

		logging.info(f"✅ Device '{name}' added successfully.")

	async def connect_devices(self):
		tasks = []
		for device in self.devices:
			try:
				logging.info(f"🚀 Starting connection for device: '{device.name}'")
				task = asyncio.create_task(device.connect())
				tasks.append(task)
			except Exception as e:
				logging.error(f"❌ Error starting connection for device: '{device.name}': {e}")
		await asyncio.gather(*tasks)

	def get_devices(self):
		return [device.name for device in self.devices]

	def get_device_config(self, name: str):
		if name not in [device.name for device in self.devices]:
			return None
		try:
			with open(os.path.join(self._devices_path, f'{name}.json'), 'r', encoding='utf-8') as f:
				data = json.load(f)
			return data
		except Exception as e:
			logging.error(f"❌ Error loading config for device '{name}': {e}")
			return None

	def get_device_types_example(self):
		"""
		Return a list of example device names from the example path.
		Only JSON files are considered, and the '.json' extension is removed.
		"""
		if not self._example_path:
			return []

		# Join example path with 'devices' folder
		devices_path = os.path.join(self._example_path, 'devices')

		if not os.path.exists(devices_path):
			return []

		return [f.replace('.json', '') for f in os.listdir(devices_path) if f.endswith('.json')]

	def get_device_config_example(self, name: str):
		"""
		Load and return the example configuration for a given device name.
		Returns None if the file does not exist or an error occurs.
		"""
		if not self._example_path:
			return None

		# Join example path with 'devices' folder
		devices_path = os.path.join(self._example_path, 'devices')
		filepath = os.path.join(devices_path, f'{name}.json')

		if not os.path.exists(filepath):
			return None

		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				data = json.load(f)
			return data
		except Exception as e:
			logging.error(f"❌ Error loading example config for device '{name}': {e}")
			return None

	def get_device_count(self):
		return len(self.devices)

	def get_device(self, name: str):
		return next((device for device in self.devices if device.name == name), None)

	def get_device_info(self, name: Optional[str] = None) -> List[Dict]:
		"""
		Return device connection and reading status.

		If name is None, returns info for all devices.
		If name is provided, returns info for the specified device only.
		"""
		if name is None:
			info_list = []
			for device in self.devices:
				info = self._get_single_device_info(device.name)
				if info:
					info_list.append(info)
			return info_list

		info = self._get_single_device_info(name)
		return [info] if info else []

	def _get_single_device_info(self, name: str) -> Optional[Dict]:
		"""
		Return information for a single device.
		"""
		device = self.get_device(name)
		if not device:
			return None

		is_connected: bool = device.is_connected
		is_reading: bool = device.is_reading if is_connected else False
		is_gpi_trigger_on: bool = getattr(device, 'is_gpi_trigger_on', False) == True
		return {
			'name': device.name,
			'is_connected': is_connected,
			'is_reading': is_reading,
			'device_type': device.device_type,
			'is_gpi_trigger_on': is_gpi_trigger_on
		}

	def any_device_reading(self) -> bool:
		"""
		Check if any device is currently reading tags.
		"""
		for device in self.devices:
			if device.is_connected and device.is_reading:
				return True
		return False

	def _validate_device_for_inventory(self, name: str, check_gpi: bool = True) -> Tuple[bool, Optional[object]]:
		"""
		Validate if a device can perform inventory operations.

		Args:
			name: Device name
			check_gpi: If True, also check if GPI trigger is on

		Returns:
			Tuple of (is_valid, device_object)
		"""
		device = self.get_device(name)
		if not device:
			logging.warning(f"⚠️ Device '{name}' not found.")
			return False, None

		if not device.device_type == 'rfid':
			logging.warning(f"⚠️ Device '{name}' is not an RFID device.")
			return False, None

		if not device.is_connected:
			logging.warning(f"⚠️ Device '{name}' is not connected.")
			return False, None

		if check_gpi and getattr(device, 'is_gpi_trigger_on', False):
			logging.warning(f"⚠️ Device '{name}' has GPI trigger on.")
			return False, None

		return True, device

	async def start_inventory(self, name: str) -> bool:
		"""
		Start inventory on the specified device.

		Returns True if the command was sent successfully, False otherwise.
		"""
		is_valid, device = self._validate_device_for_inventory(name, check_gpi=True)
		if not is_valid:
			return False

		try:
			await device.start_inventory()
			logging.info(f"✅ Starting inventory on device '{name}'.")
			return True
		except Exception as e:
			logging.error(f"❌ Error starting inventory on device '{name}': {e}")
			return False

	async def stop_inventory(self, name: str) -> bool:
		"""
		Stop inventory on the specified device.

		Returns True if the command was sent successfully, False otherwise.
		"""
		is_valid, device = self._validate_device_for_inventory(name)
		if not is_valid:
			return False

		try:
			await device.stop_inventory()
			logging.info(f"✅ Stopping inventory on device '{name}'.")
			return True
		except Exception as e:
			logging.error(f"❌ Error stopping inventory on device '{name}': {e}")
			return False

	async def start_inventory_all(self) -> Dict[str, bool]:
		"""
		Start inventory on all connected RFID devices.

		Returns a dictionary with device names as keys and success status as values.
		"""
		results = {}
		for device in self.devices:
			if device.device_type == 'rfid' and device.is_connected:
				if not getattr(device, 'is_gpi_trigger_on', False):
					success = await self.start_inventory(device.name)
					results[device.name] = success
				else:
					logging.info(f"⚠️ Skipping device '{device.name}' (GPI trigger is on).")
					results[device.name] = False
		return results

	async def stop_inventory_all(self) -> Dict[str, bool]:
		"""
		Stop inventory on all connected RFID devices.

		Returns a dictionary with device names as keys and success status as values.
		"""
		results = {}
		for device in self.devices:
			if device.device_type == 'rfid' and device.is_connected:
				success = await self.stop_inventory(device.name)
				results[device.name] = success
		return results
	

	async def write_epc(self, device_name: str, write_tag: WriteTagValidator) -> Tuple[bool, Optional[str]]:
		device = self.get_device(device_name)
		if device is None:
			return False, f"Device '{device_name}' not found."
		
		if not getattr(device, "write_epc", None):
			return False, f"Device '{device_name}' does not support writing EPC."
		
		try:
			await device.write_epc(**write_tag.model_dump())
			return True, None
		except Exception as e:
			return False, str(e)