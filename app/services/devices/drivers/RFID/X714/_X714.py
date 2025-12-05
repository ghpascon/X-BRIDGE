import asyncio
from app.services.events import events
from .on_receive import OnReceive
from .rfid import RfidCommands
from .serial_protocol import SerialProtocol
from .ble_protocol import BLEProtocol
from .write_commands import WriteCommands
from .tcp_protocol import TCPProtocol
import logging

class X714(SerialProtocol, OnReceive, RfidCommands, BLEProtocol, WriteCommands, TCPProtocol):
    def __init__(self, config, name):
        self.is_rfid_reader = True

        self.name = name
        self.config = config

        # CONNECTION TYPE
        self.connection_type = self.config.get("CONNECTION_TYPE")
        if self.connection_type not in config.get("_CONNECTION_TYPE", []):
            self.connection_type = "SERIAL"

        self.tcp_port = self.config.get("TCP_PORT", 23)

        self.ble_name = self.config.get("BLE_NAME", "SMTX")
        self.init_ble_vars()

        self.connection = self.config.get("CONNECTION", "AUTO")
        self.baudrate = self.config.get("BAUDRATE", 115200)
        self.vid = self.config.get("VID", 1)
        self.pid = self.config.get("PID", 1)

        self.transport = None
        self.on_con_lost = None
        self.rx_buffer = bytearray()
        self.last_byte_time = None

        self.is_connected = False
        self.is_reading = False

        self.is_auto = self.connection == "AUTO"
        self.init_ble_vars()

    def write(self, to_send, verbose=True):
        if self.connection_type == "SERIAL":
            self.write_serial(to_send, verbose)
        elif self.connection_type == "BLE":
            asyncio.create_task(self.write_ble(to_send.encode(), verbose))
        else:
            asyncio.create_task(self.write_tcp(to_send, verbose))

    async def connect(self):
        if self.connection_type == "SERIAL":
            await self.connect_serial()
        elif self.connection_type == "BLE":
            await self.connect_ble()
        else:
            await self.connect_tcp(self.connection, self.tcp_port)

    def on_connected(self):
        """Callback chamado quando a conexão é estabelecida."""
        asyncio.create_task(self.config_reader())
        asyncio.create_task(events.on_connect(self.name))