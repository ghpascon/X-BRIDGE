import json
import logging
import os
from pathlib import Path

from app.core import settings
from app.core import DEVICES_PATH, EXAMPLE_PATH
from app.services import rfid_manager
import asyncio


class SettingsService:
    def __init__(self):
        self.has_changes: bool = False

    def update_settings(self, data: dict):
        settings.load(data)
        settings.save()
        self.has_changes = True

    def reload_devices(self):
        asyncio.create_task(rfid_manager.devices.cancel_connect_tasks())

    def create_device(self, device_name: str, data: dict) -> tuple[bool, str | None]:
        try:
            Path(DEVICES_PATH).mkdir(parents=True, exist_ok=True)

            device_path = os.path.join(DEVICES_PATH, f'{device_name}.json')

            if os.path.exists(device_path):
                return False, 'Device already exists'

            with open(device_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            logging.info(f'Device created: {device_name}')

            self.reload_devices()
            return True, None
        except Exception as e:
            return False, str(e)

    def update_device(self, device_name: str, data: dict) -> tuple[bool, str | None]:
        try:
            device_path = os.path.join(DEVICES_PATH, f'{device_name}.json')

            if not os.path.exists(device_path):
                return False, 'Device does not exist'

            with open(device_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            logging.info(f'Device updated: {device_name}')

            self.reload_devices()
            return True, None
        except Exception as e:
            return False, str(e)

    def delete_device(self, device_name: str) -> tuple[bool, str | None]:
        try:
            device_path = os.path.join(DEVICES_PATH, f'{device_name}.json')

            if not os.path.exists(device_path):
                return False, 'Device does not exist'

            os.remove(device_path)
            logging.info(f'Device deleted: {device_name}')

            self.reload_devices()
            return True, None
        except Exception as e:
            return False, str(e)

    def _get_example_config(self) -> dict:
        try:
            config_path = os.path.join(EXAMPLE_PATH, 'config.json')
            if not os.path.exists(config_path):
                return {}

            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {key: value for key, value in data.items() if not key.startswith('_')}
        except Exception:
            return {}
