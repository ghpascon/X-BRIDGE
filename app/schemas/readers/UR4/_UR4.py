import asyncio
from app.core.config import settings
from app.schemas.logger import log_error,log_info
from .helpers import ReaderHelpers
from .on_event import OnEvent
from .setup_reader import SetupReader
from datetime import datetime
from app.db.database import get_db
from app.models.rfid import DbTag
from .write_commands import WriteCommands
from ...rfid import rfid

class UR4(ReaderHelpers, OnEvent, SetupReader, WriteCommands):
    def __init__(self, config):
        self.config = config
        self.device_name = self.config.get("NAME")

        self.ip = self.config.get("CONNECTION")
        self.port = self.config.get("PORT", 8888) 

        self.reader = None
        self.writer = None

        self.tags_to_write = {}

        self.is_connected = False
        self.is_reading = False

        self.setup = False
        self.setup_step = 0 
        self.wait_answer = False
        self.current_timeout_answer = 0
        self.timeout_answer = 500

        self.ant_qtd = 4
        self.min_power = 10
        self.max_power = 30

        self.temperature = 0

        self.gpi = {"1":False, "2":False}
        self.gpi_config = self.config.get("GPI")

    async def connect(self):
        while True:
            try:
                print(f"Tentando conectar ao leitor em {self.ip}:{self.port}")
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.ip, self.port), timeout=3
                )
                self.is_connected = True
                log_info(f"✅ [CONECTADO] Conectado a {self.ip}:{self.port}")

                # Rode as tarefas de forma independente para monitorar desconexão
                tasks = [
                    asyncio.create_task(self.receive_data()),
                    asyncio.create_task(self.setup_reader()),
                    asyncio.create_task(self.monitor_connection()),
                    asyncio.create_task(self.get_temperature()),
                    asyncio.create_task(self.get_gpi_state()),
                    asyncio.create_task(self.ensure_reading_command()),
                ]

                # Aguarde até que uma das tarefas termine (ex: desconexão)
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                # Cancela todas as tarefas restantes
                for task in pending:
                    task.cancel()

                self.is_connected = False
                log_info("Conexão perdida, tentando reconectar...")

            except Exception as e:
                self.is_connected = False
                log_error(f"❌ Erro: {e}. Tentando reconectar em 3 segundos...")

            await asyncio.sleep(3)

    async def send_data(self, data, verbose = True):
        if self.is_connected and self.writer:
            try:
                data[-3] = await self.get_bcc(data)
                data = bytes(data)
                self.writer.write(data)
                await self.writer.drain()
                if verbose:
                    log_info(f"[ENVIADO] {' '.join(f'{b:02x}' for b in data)}")
            except Exception as e:
                log_error(f"[ERRO ENVIO] {e}")
                self.is_connected = False

    async def start_inventory(self):
        if self.is_reading: return
        await rfid.clear_tags(self.device_name)
        await self.send_data([0xa5, 0x5a, 0x00, 0x0a, 0x82, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        self.is_reading = True
        log_info("[ START ]")

    async def stop_inventory(self):
        if not self.is_reading: return
        await self.send_data([0xa5, 0x5a, 0x00, 0x08, 0x8c, 0x00, 0x0d, 0x0a])
        await self.send_data([0xa5, 0x5a, 0x00, 0x09, 0x8d, 0x01, 0x00, 0x0d, 0x0a])
               
        self.is_reading = False
        log_info("[ STOP ]")

    async def set_gpo(self, state=False):
        await self.send_data([0xa5, 0x5a, 0x00, 0x0c, 0xa1, 0x09, 0x00, 0x00, 0x00 if not state else 0x01, 0x00, 0x0d, 0x0a])
        
    async def get_connected(self):
        await self.send_data([0xa5, 0x5a, 0x00, 0x08, 0x4e, 0x00, 0x0d, 0x0a])
        
    # async def save_tags(self):
    #     try:
    #         time = datetime.now()
    #         async with get_db() as db:
    #             for epc in self.tags:
    #                 tag = self.tags.get(epc)
    #                 current_tag = DbTag(
    #                     datetime = time,                 
    #                     epc = tag.get("epc"),           
    #                     tid = tag.get("tid"),
    #                     ant = tag.get("ant"),
    #                     rssi = tag.get("rssi"),                       
    #                 )
    #                 if current_tag.epc is None:
    #                     continue
    #                 db.add(current_tag)

    #             await db.commit()
    #             print("Tags salvas")

    #     except Exception as e:
    #         log_error(f"Erro ao salvar tags: {e}")

