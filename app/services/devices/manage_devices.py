import asyncio
import json
import logging
import os
from typing import Any, Dict


class ManageDevices:
    def __init__(self):
        self.devices = {}
        self.connect_task = None
        self.device_tasks: Dict[str, asyncio.Task] = {}
        self._shutdown_event = asyncio.Event()
        self._updating = False

    def ensure_devices_path(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                logging.info(f"📁 Diretório criado: {path}")
        except Exception as e:
            logging.error(f"❌ Erro ao criar/verificar diretório '{path}': {e}")
            raise

    async def connect_loop(self):
        """Cria e gerencia as tasks de conexão para todos os devices."""
        logging.info("🔄 Iniciando loop de conexão para todos os devices")

        for name, device in self.devices.items():
            if name not in self.device_tasks or self.device_tasks[name].done():
                try:
                    logging.info(f"🚀 Iniciando conexão para '{name}'")
                    task = asyncio.create_task(device.connect())
                    self.device_tasks[name] = task
                except Exception as e:
                    logging.error(f"❌ Erro ao iniciar conexão para '{name}': {e}")

        # Aguarda até que seja solicitado o shutdown
        try:
            await self._shutdown_event.wait()
        except asyncio.CancelledError:
            logging.info("🛑 Connect loop cancelado")

    async def create_connect_loop(self):
        self.connect_task = asyncio.create_task(self.connect_loop())

    async def _disconnect_device(self, name: str, device: Any) -> None:
        """Desconecta um device específico de forma segura."""
        try:
            logging.info(f"🔌 Desconectando device '{name}'")

            # Cancela a task de conexão se existir
            if name in self.device_tasks:
                task = self.device_tasks[name]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self.device_tasks[name]

            # Desconecta o device se tiver métodos de desconexão
            if hasattr(device, "disconnect"):
                await device.disconnect()
            elif hasattr(device, "transport") and device.transport:
                device.transport.close()
            elif hasattr(device, "writer") and device.writer:
                device.writer.close()
                await device.writer.wait_closed()
            elif hasattr(device, "client_ble") and device.client_ble:
                await device.client_ble.disconnect()

            # Marca como desconectado
            if hasattr(device, "is_connected"):
                device.is_connected = False

            logging.info(f"✅ Device '{name}' desconectado com sucesso")

        except Exception as e:
            logging.error(f"❌ Erro ao desconectar device '{name}': {e}")

    async def _disconnect_all_devices(self) -> None:
        """Desconecta todos os devices de forma segura."""
        logging.info("🔌 Desconectando todos os devices")

        disconnect_tasks = []
        for name, device in self.devices.items():
            task = asyncio.create_task(self._disconnect_device(name, device))
            disconnect_tasks.append(task)

        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)

        # Limpa todas as tasks restantes
        self.device_tasks.clear()

        logging.info("✅ Todos os devices desconectados")

    async def restart_connect_loop(self):
        """Reinicia o loop de conexão de forma segura."""
        try:
            self._updating = True
            logging.info("🔄 Reiniciando loop de conexão")

            # Sinaliza para parar o loop atual
            self._shutdown_event.set()

            # Aguarda o loop atual terminar
            if self.connect_task and not self.connect_task.done():
                try:
                    await asyncio.wait_for(self.connect_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logging.warning(
                        "⏰ Timeout ao aguardar loop de conexão, cancelando forcosamente"
                    )
                    self.connect_task.cancel()
                    try:
                        await self.connect_task
                    except asyncio.CancelledError:
                        pass

            # Desconecta todos os devices ativos
            await self._disconnect_all_devices()

            # Reset do evento e recria o loop
            self._shutdown_event.clear()
            await self.create_connect_loop()

        except Exception as e:
            logging.error(f"❌ Erro ao reiniciar loop de conexão: {e}")
        finally:
            self._updating = False

    async def create_device(self, data, name="default", path="config/devices"):
        self.ensure_devices_path(path)
        name = self._generate_unique_name(name)
        filename = f"{path}/{name}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            self.get_devices_from_config()
            await self.restart_connect_loop()
            return {"msg": f"{name} created"}
        except Exception as e:
            logging.error("❌ Erro ao criar o dispositivo:", e)
            return {"error": str(e)}

    async def update_device(self, data, name="default", path="config/devices"):
        """Atualiza um device de forma segura, desconectando antes da atualização."""
        self.ensure_devices_path(path)
        name = name.upper()
        filename = f"{path}/{name}.json"

        # Previne atualizações concorrentes
        if self._updating:
            return {
                "error": "Sistema em processo de atualização, tente novamente em alguns segundos"
            }

        try:
            # Se o device já existe, desconecta ele primeiro
            if name in self.devices:
                logging.info(f"📝 Atualizando device existente: {name}")
                await self._disconnect_device(name, self.devices[name])

            # Salva a nova configuração
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            logging.info(f"💾 Configuração salva para {name}")

            # Recarrega a configuração e reinicia as conexões
            self.get_devices_from_config()
            await self.restart_connect_loop()

            return {"msg": f"{name} updated"}

        except Exception as e:
            logging.error(f"❌ Erro ao atualizar o dispositivo {name}: {e}")
            return {"error": str(e)}

    async def delete_device(self, name="default", path="config/devices"):
        """Deleta um device de forma segura, desconectando antes da remoção."""
        self.ensure_devices_path(path)
        name = name.upper()
        filename = f"{path}/{name}.json"

        # Previne operações concorrentes
        if self._updating:
            return {
                "error": "Sistema em processo de atualização, tente novamente em alguns segundos"
            }

        try:
            if not os.path.exists(filename):
                return {"error": f"Dispositivo '{name}' não encontrado."}

            # Se o device está ativo, desconecta primeiro
            if name in self.devices:
                logging.info(f"🗑️ Deletando device: {name}")
                await self._disconnect_device(name, self.devices[name])

            # Remove o arquivo de configuração
            os.remove(filename)
            logging.info(f"🗑️ Arquivo '{filename}' removido.")

            # Recarrega a configuração e reinicia as conexões
            self.get_devices_from_config()
            await self.restart_connect_loop()

            return {"msg": f"{name} deleted"}

        except Exception as e:
            logging.error(f"❌ Erro ao deletar o dispositivo {name}: {e}")
            return {"error": str(e)}
