import json
import os

import logging

from .add_device import AddDevice
from .devices_commands import DevicesCommands
from .manage_devices import ManageDevices


class Devices(AddDevice, DevicesCommands, ManageDevices):
    def __init__(self):
        self.devices = {}
        self.connect_task = None
        self.get_devices_from_config()

    def _generate_unique_name(self, base_name):
        base_name = base_name.upper()
        if base_name not in self.devices:
            return base_name

        index = 2
        new_name = f"{base_name}_{index}"
        while new_name in self.devices:
            index += 1
            new_name = f"{base_name}_{index}"
        return new_name

    def get_devices_from_config(self, devices_path="config/devices"):
        print("DEVICES:")
        self.devices = {}

        try:
            # Verifica se o diretório existe; se não, cria
            if not os.path.exists(devices_path):
                os.makedirs(devices_path)
                logging.info(f"📁 Diretório criado: {devices_path}")
        except Exception as e:
            logging.error(f"❌ Erro ao verificar/criar diretório '{devices_path}': {e}")
            return

        for filename in os.listdir(devices_path):
            if filename.endswith(".json"):
                filepath = os.path.join(devices_path, filename)
                print(f"📄 Arquivo: {filename}")
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("READER") is None:
                        os.remove(filepath)
                        continue
                    name = filename.replace(".json", "")
                    self.add_device(data, name)
                except json.JSONDecodeError as e:
                    logging.error(f"❌ Erro ao carregar JSON: {e}")
                except Exception as e:
                    logging.error(f"❌ Erro ao processar o arquivo '{filename}': {e}")

    async def get_device_types(self, path="config/device_examples"):
        try:
            filenames = []
            for file in os.listdir(path):
                if file.endswith(".json"):
                    filenames.append(os.path.splitext(file)[0])
            return filenames
        except Exception as e:
            return {"error": str(e)}

    async def get_example_config(self, device, path="config/device_examples"):
        try:
            path += f"/{device}.json"
            with open(path, "r") as f:
                content = json.load(f)
                return content
        except Exception as e:
            return {"error": "Device not found"}


devices = Devices()
