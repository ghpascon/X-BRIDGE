import asyncio
import serial.tools.list_ports
import serial_asyncio

import logging

from .on_receive import OnReceive
from .rfid import RfidCommands


class X714(asyncio.Protocol, OnReceive, RfidCommands):
    def __init__(self, config, name):
        self.is_rfid_reader = True

        self.config = config
        self.port = self.config.get("CONNECTION")
        self.baudrate = self.config.get("BAUDRATE")
        self.vid = self.config.get("VID", 1)
        self.pid = self.config.get("PID", 1)
        self.name = name

        self.transport = None
        self.on_con_lost = None
        self.rx_buffer = bytearray()
        self.last_byte_time = None

        self.is_connected = False
        self.is_reading = False

        self.is_auto = self.port == "AUTO"

    def connection_made(self, transport):
        self.transport = transport
        self.is_connected = True
        logging.info("✅ Serial connection successfully established.")
        asyncio.create_task(self.config_reader())

    def data_received(self, data):
        self.rx_buffer += data

        while b"\n" in self.rx_buffer:
            idx = self.rx_buffer.index(b"\n")
            packet = self.rx_buffer[:idx]
            self.rx_buffer = self.rx_buffer[idx + 1 :]
            asyncio.create_task(self.on_receive(packet))

    def connection_lost(self, exc):
        logging.error("⚠️ Serial connection lost.")
        self.transport = None
        self.is_connected = False

        if self.on_con_lost:
            self.on_con_lost.set()

    def write(self, to_send, verbose=True):
        if self.transport:
            if verbose:
                logging.info(f"📤 Sending: {to_send}")
            if isinstance(to_send, str):
                to_send += "\n"
                to_send = to_send.encode()  # convert string to bytes
            self.transport.write(to_send)
        else:
            logging.error("❌ Send attempt failed: connection not established.")

    async def connect(self):
        """Serial connection/reconnection loop"""
        loop = asyncio.get_running_loop()

        while True:
            self.on_con_lost = asyncio.Event()

            # If AUTO mode, try to detect port by VID/PID
            if self.is_auto:
                print("🔍 Auto-detecting port by VID=0001 and PID=0001...")
                ports = serial.tools.list_ports.comports()
                found_port = None
                for p in ports:
                    # p.vid and p.pid are integers (e.g. 0x0001 == 1 decimal)
                    if p.vid == self.vid and p.pid == self.pid:
                        found_port = p.device
                        print(f"✅ Detected port: {found_port}")
                        break

                if found_port is None:
                    print(f"⚠️ No port with VID={self.vid} and PID={self.pid} found.")
                    print("⏳ Retrying in 3 seconds...")
                    await asyncio.sleep(3)
                    continue  # try to detect again in next loop
                else:
                    self.port = found_port

            try:
                print(f"🔌 Trying to connect to {self.port} at {self.baudrate} bps...")
                await serial_asyncio.create_serial_connection(
                    loop, lambda: self, self.port, baudrate=self.baudrate
                )
                logging.info("🟢 Successfully connected.")
                await self.on_con_lost.wait()
                print("🔄 Connection lost. Attempting to reconnect...")
            except Exception as e:
                logging.error(f"❌ Connection error: {e}")

            # If in AUTO mode, reset port to "AUTO" to force detection next loop
            if self.is_auto:
                self.port = "AUTO"

            print("⏳ Waiting 3 seconds before retrying...")
            await asyncio.sleep(3)
