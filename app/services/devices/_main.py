import asyncio
import json
import logging
import os

from .add_device import AddDevice
from .devices_commands import DevicesCommands
from .manage_devices import ManageDevices


class Devices(AddDevice, DevicesCommands, ManageDevices):
    """
    The Devices class manages device configurations,
    loading them from JSON files, and providing utility
    functions to handle device data.
    """

    def __init__(self):
        """
        Initialize the Devices manager.
        - Loads devices from the configuration folder.
        """
        self.devices = {}
        self.connect_task = None
        self.device_tasks = {}
        self._shutdown_event = asyncio.Event()
        self._updating = False
        self._initialized = False

        try:
            self.get_devices_from_config()
            self._initialized = True
            logging.info("✅ Devices manager initialized successfully")
        except Exception as e:
            logging.error(f"❌ Failed to initialize Devices manager: {e}")

    def _generate_unique_name(self, base_name):
        """
        Generate a unique device name based on the given base name.
        If the name already exists, add an incrementing index.

        Args:
            base_name (str): Suggested name for the device.

        Returns:
            str: A unique device name.
        """
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
        """
        Load devices from JSON configuration files in the given directory.
        If the directory does not exist, it will be created.

        Args:
            devices_path (str): Path to the directory containing device config files.
        """
        logging.info("🔄 Loading devices from configuration...")

        # Armazena devices antigos para comparação
        old_devices = dict(self.devices)
        self.devices = {}

        devices_loaded = 0
        devices_failed = 0

        try:
            # Create directory if it does not exist
            if not os.path.exists(devices_path):
                os.makedirs(devices_path)
                logging.info(f"📁 Directory created: {devices_path}")
        except Exception as e:
            logging.error(f"❌ Error checking/creating directory '{devices_path}': {e}")
            # Restaura devices antigos em caso de erro
            self.devices = old_devices
            return

        # Iterate over JSON files in the directory
        for filename in os.listdir(devices_path):
            if filename.endswith(".json"):
                filepath = os.path.join(devices_path, filename)
                logging.info(f"📄 Processing file: {filename}")

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Validate basic structure
                    if not isinstance(data, dict):
                        logging.warning(
                            f"⚠️ Invalid config format in '{filename}': not a JSON object"
                        )
                        devices_failed += 1
                        continue

                    # If the device config is invalid, remove the file
                    if data.get("READER") is None:
                        logging.warning(
                            f"⚠️ Invalid config in '{filename}': missing READER field, removing file"
                        )
                        os.remove(filepath)
                        devices_failed += 1
                        continue

                    name = filename.replace(".json", "")

                    # Tenta adicionar o device
                    if self.add_device(data, name):
                        devices_loaded += 1
                    else:
                        devices_failed += 1

                except json.JSONDecodeError as e:
                    logging.error(f"❌ JSON decode error in '{filename}': {e}")
                    devices_failed += 1
                except FileNotFoundError:
                    logging.warning(f"⚠️ File disappeared during processing: '{filename}'")
                    devices_failed += 1
                except Exception as e:
                    logging.error(f"❌ Error processing file '{filename}': {e}")
                    devices_failed += 1

        logging.info(f"📊 Device loading summary: {devices_loaded} loaded, {devices_failed} failed")

        if devices_loaded == 0 and devices_failed > 0:
            logging.warning("⚠️ No devices loaded successfully, restoring previous configuration")
            self.devices = old_devices

    async def get_device_types(self, path="config/examples/device_examples"):
        """
        List available device types from example JSON files.

        Args:
            path (str): Path to the folder containing example device configs.

        Returns:
            list | dict: List of device type names or error dictionary.
        """
        try:
            filenames = []
            for file in os.listdir(path):
                if file.endswith(".json"):
                    filenames.append(os.path.splitext(file)[0])
            return filenames
        except Exception as e:
            return {"error": str(e)}

    async def get_example_config(self, device, path="config/examples/device_examples"):
        """
        Load and return the content of an example device configuration.

        Args:
            device (str): The device type (filename without extension).
            path (str): Path to the folder containing example configs.

        Returns:
            dict: JSON content of the example config or an error message.
        """
        try:
            path += f"/{device}.json"
            with open(path, "r") as f:
                content = json.load(f)
                return content
        except Exception:
            return {"error": "Device not found"}

    def get_system_status(self):
        """Retorna o status completo do sistema de devices."""
        connected_count = sum(
            1
            for device in self.devices.values()
            if hasattr(device, "is_connected") and device.is_connected
        )
        reading_count = sum(
            1
            for device in self.devices.values()
            if hasattr(device, "is_reading") and device.is_reading
        )

        return {
            "total_devices": len(self.devices),
            "connected_devices": connected_count,
            "reading_devices": reading_count,
            "updating": self._updating,
            "initialized": self._initialized,
            "connect_task_running": self.connect_task and not self.connect_task.done(),
        }

    async def shutdown(self):
        """Shutdown seguro de todo o sistema de devices."""
        logging.info("🛑 Iniciando shutdown do sistema de devices...")

        try:
            self._updating = True

            # Para o loop principal
            if self.connect_task and not self.connect_task.done():
                self._shutdown_event.set()
                await self.connect_task

            # Desconecta todos os devices
            await self._disconnect_all_devices()

            logging.info("✅ Shutdown do sistema de devices concluído")

        except Exception as e:
            logging.error(f"❌ Erro durante shutdown: {e}")
        finally:
            self._updating = False


devices = Devices()
