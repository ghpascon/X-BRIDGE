import os
import json
from app.schemas.logger import log_error
from .add_device import AddDevice
from .devices_commands import DevicesCommands

class Devices(AddDevice, DevicesCommands):
    def __init__(self, devices_path):
        self.devices = {}
        self.get_devices_from_config(devices_path)

    def get_devices_from_config(self, devices_path):
        print("DEVICES:")
        for filename in os.listdir(devices_path):
            if filename.endswith('.json'):
                filepath = os.path.join(devices_path, filename)
                print(f'📄 Arquivo: {filename}')
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        self.add_device(data)
                    except json.JSONDecodeError as e:
                        log_error(f'❌ Erro ao carregar JSON: {e}')


devices = Devices('config/devices')