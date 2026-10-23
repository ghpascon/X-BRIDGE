import asyncio

import pytest
from smartx_rfid.utils import TagList

from app.services.rfid import controller as controller_module
from app.services.rfid import integration as integration_module
from app.services.rfid._main import RfidManager
from app.services.rfid.controller import Controller
from app.services.rfid.integration import Integration


class FakeDevices:
	def __init__(self, serials: dict | None = None):
		self.serials = serials or {}

	def get_serial_number(self, name: str):
		serial = self.serials.get(name)
		return (True, serial) if serial else (False, 'Device not found.')


class FakeController:
	def __init__(self):
		self.calls: list[tuple] = []

	def on_event(self, device, event_type, event_data):
		self.calls.append(('event', device, event_type, event_data))

	def on_start(self, device):
		self.calls.append(('start', device))

	def on_stop(self, device):
		self.calls.append(('stop', device))

	def on_new_tag(self, device, tag):
		self.calls.append(('new_tag', device, tag))

	def on_existing_tag(self, device, tag):
		self.calls.append(('existing_tag', device, tag))


@pytest.fixture
def manager():
	manager = RfidManager.__new__(RfidManager)
	manager.tags = TagList(unique_identifier='tid')
	manager.devices = FakeDevices({'reader-01': 'SN-001'})
	manager.controller = FakeController()
	return manager


def test_build_device_resolves_serial_number(manager):
	assert manager.build_device('reader-01') == {'name': 'reader-01', 'serial_number': 'SN-001'}


def test_build_device_unknown_device_has_no_serial_number(manager):
	assert manager.build_device('other') == {'name': 'other', 'serial_number': None}


def test_build_device_prefers_explicit_serial_number(manager):
	assert manager.build_device('reader-01', 'SN-XYZ')['serial_number'] == 'SN-XYZ'


def test_on_event_routes_tag_with_device_dict(manager):
	device = {'name': 'reader-01', 'serial_number': 'SN-001'}
	tag_data = {'epc': 'a' * 24, 'tid': 'e' * 24, 'ant': 1, 'rssi': -50}

	manager.on_event(device, 'tag', tag_data)

	kind, called_device, tag = manager.controller.calls[0]
	assert kind == 'new_tag'
	assert called_device == device
	assert tag['device'] == 'reader-01'
	assert tag['device_serial_number'] == 'SN-001'


def test_on_event_accepts_plain_string_device(manager):
	manager.on_event('reader-01', 'connection', True)

	assert manager.controller.calls == [
		('event', {'name': 'reader-01', 'serial_number': None}, 'connection', True)
	]


def test_on_event_reading_triggers_start_and_stop(manager):
	device = {'name': 'reader-01', 'serial_number': None}

	manager.on_event(device, 'reading', True)
	manager.on_event(device, 'reading', False)

	kinds = [call[0] for call in manager.controller.calls]
	assert kinds == ['start', 'event', 'stop', 'event']


def test_existing_tag_is_routed_as_existing(manager):
	device = {'name': 'reader-01', 'serial_number': 'SN-001'}
	tag_data = {'epc': 'a' * 24, 'tid': 'e' * 24, 'ant': 1, 'rssi': -50}

	manager.on_tag(device, dict(tag_data))
	manager.on_tag(device, dict(tag_data))

	assert [call[0] for call in manager.controller.calls] == ['new_tag', 'existing_tag']


def test_xscan_event_uses_device_serial_number(manager):
	manager.on_xscan_event(
		device_name='scanner',
		event_type='inventory',
		event_data={'tags': [{'epc': 'a' * 24, 'tid': 'e' * 24, 'read_count': 3}]},
		device_serial_number='SN-SCAN',
	)

	kind, device, tag = manager.controller.calls[0]
	assert device == {'name': 'scanner', 'serial_number': 'SN-SCAN'}
	assert tag['count'] == 3


def test_r700_event_builds_device_from_hostname(manager):
	manager.handle_r700_event(
		[
			{
				'eventType': 'inventoryStatus',
				'hostname': 'reader-01',
				'inventoryStatusEvent': {'inventoryStatus': 'running'},
			}
		]
	)

	assert manager.controller.calls[0] == (
		'start',
		{'name': 'reader-01', 'serial_number': 'SN-001'},
	)


def test_controller_forwards_device_dict(monkeypatch):
	asyncio.run(_check_controller_forwards_device_dict(monkeypatch))


async def _check_controller_forwards_device_dict(monkeypatch):
	monkeypatch.setattr(controller_module.license_manager, 'validate_license', lambda: True)
	received = {}

	class StubIntegration:
		async def on_event_integration(self, device, event_type, event_data):
			received['integration'] = (device, event_type, event_data)

	class StubDispatcher:
		async def add_async(self, device, event_type, data=None):
			received['dispatcher'] = (device, event_type, data)

	controller = Controller.__new__(Controller)
	controller.integration = StubIntegration()
	controller.dispatcher = StubDispatcher()

	device = {'name': 'reader-01', 'serial_number': 'SN-001'}
	controller.on_event(device=device, event_type='connection', event_data=True)
	await asyncio.sleep(0)
	await asyncio.sleep(0)

	assert received['integration'] == (device, 'connection', True)
	assert received['dispatcher'] == (device, 'connection', True)


def test_integration_forwards_device_dict_to_webhook(monkeypatch):
	asyncio.run(_check_integration_forwards_device_dict_to_webhook(monkeypatch))


async def _check_integration_forwards_device_dict_to_webhook(monkeypatch):
	monkeypatch.setattr(integration_module.license_manager, 'validate_license', lambda: True)
	monkeypatch.setattr(integration_module.settings, 'BEEP', False)
	monkeypatch.setattr(Integration, 'setup_integration', lambda self: None)
	posted = []

	class StubWebhook:
		async def post_event(self, device, event_type, event_data):
			posted.append((device, event_type, event_data))

	integration = Integration()
	integration.webhook_manager = StubWebhook()

	device = {'name': 'reader-01', 'serial_number': 'SN-001'}
	await integration.on_event_integration(device, 'reading', True)
	await integration.on_tag_integration(
		{'device': 'reader-01', 'device_serial_number': 'SN-001', 'epc': 'ABC'}
	)

	assert posted[0] == (device, 'reading', True)
	assert posted[1][0] == device
	assert posted[1][1] == 'tag'
