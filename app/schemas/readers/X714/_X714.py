import asyncio
import time

import serial_asyncio

from app.core.config import settings
import logging

from .on_receive import OnReceive
from .rfid import RfidCommands


class X714(asyncio.Protocol, OnReceive, RfidCommands):
    def __init__(self, config, name):
        self.config = config
        self.port = self.config.get("CONNECTION")
        self.baudrate = self.config.get("BAUDRATE")
        self.name = name

        self.transport = None
        self.on_con_lost = None
        self.rx_buffer = bytearray()
        self.last_byte_time = None

        self.is_connected = False
        self.is_reading = False

    def connection_made(self, transport):
        self.transport = transport
        self.is_connected = True
        logging.info("✅ Conexão serial estabelecida com sucesso.")
        asyncio.create_task(self.config_reader())

    def data_received(self, data):
        self.rx_buffer += data

        while b"\n" in self.rx_buffer:
            idx = self.rx_buffer.index(b"\n")
            pacote = self.rx_buffer[:idx]
            self.rx_buffer = self.rx_buffer[idx + 1 :]
            asyncio.create_task(self.on_receive(pacote))

    def connection_lost(self, exc):
        logging.error("⚠️ Conexão serial perdida.")
        self.transport = None
        self.is_connected = False

        if self.on_con_lost:
            self.on_con_lost.set()

    def write(self, to_send, verbose=True):
        if self.transport:
            if verbose:
                logging.info(f"📤 Enviando: {to_send}")
            if isinstance(to_send, str):
                to_send += "\n"
                to_send = to_send.encode()  # converte string para bytes
            self.transport.write(to_send)
        else:
            logging.error("❌ Tentativa de envio falhou: conexão não estabelecida.")

    async def connect(self):
        """Loop de conexão/reconexão serial"""
        loop = asyncio.get_running_loop()

        while True:
            self.on_con_lost = asyncio.Event()

            try:
                print(f"🔌 Tentando conectar em {self.port} a {self.baudrate} bps...")
                await serial_asyncio.create_serial_connection(
                    loop, lambda: self, self.port, baudrate=self.baudrate
                )
                logging.info("🟢 Conectado com sucesso.")
                await self.on_con_lost.wait()
                print("🔄 Conexão perdida. Tentando reconectar...")
            except Exception as e:
                logging.error(f"❌ Erro ao conectar: {e}")

            print("⏳ Aguardando 3 segundos antes de tentar novamente...")
            await asyncio.sleep(3)
