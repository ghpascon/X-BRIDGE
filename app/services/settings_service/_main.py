import json
import os
from pathlib import Path

from app.core import settings
from app.core import DEVICES_PATH, EXAMPLE_PATH


class SettingsService:
    def __init__(self):
        self.has_changes: bool = False

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if callable(attr) and not name.startswith('_'):
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                object.__setattr__(self, 'has_changes', True)
                return result
            return wrapper
        return attr

    def update_settings(self, data: dict):
        settings.load(data)
        settings.save()

    def create_device(self, device_name: str, data: dict) -> tuple[bool, str | None]:
        try:
            Path(DEVICES_PATH).mkdir(parents=True, exist_ok=True)
            
            device_path = os.path.join(DEVICES_PATH, f"{device_name}.json")
            
            if os.path.exists(device_path):
                return False, "Device already exists"
            
            with open(device_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True, None
        except Exception as e:
            return False, str(e)

    def update_device(self, device_name: str, data: dict) -> tuple[bool, str | None]:
        try:
            device_path = os.path.join(DEVICES_PATH, f"{device_name}.json")
            
            if not os.path.exists(device_path):
                return False, "Device does not exist"
            
            with open(device_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True, None
        except Exception as e:
            return False, str(e)

    def delete_device(self, device_name: str) -> tuple[bool, str | None]:
        try:
            device_path = os.path.join(DEVICES_PATH, f"{device_name}.json")
            
            if not os.path.exists(device_path):
                return False, "Device does not exist"
            
            os.remove(device_path)
            
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
            
            return {
                key: value
                for key, value in data.items()
                if not key.startswith('_')
            }
        except Exception as e:
            return {}