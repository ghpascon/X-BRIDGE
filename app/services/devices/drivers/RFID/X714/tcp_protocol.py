import asyncio
import logging
from app.services.events import events
import socket

class TCPHelpers:
    async def monitor_connection(self):
        while self.is_connected:
            await asyncio.sleep(3)
            if (self.writer and self.writer.is_closing()) or (self.reader and self.reader.at_eof()):
                self.is_connected = False
                logging.info("[DISCONNECTED] Socket closed.")
                break

            await self.write_tcp("ping", verbose=False)

    async def receive_data_tcp(self):
        buffer = ""
        try:
            while True:
                try:
                    data = await asyncio.wait_for(self.reader.read(1024), timeout=0.1)
                except asyncio.TimeoutError:
                    # Timeout: process what's in the buffer as a command
                    if buffer:
                        await self.on_receive(buffer.strip())
                        buffer = ""
                    continue

                if not data:
                    raise ConnectionError("Connection lost")

                buffer += data.decode(errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    await self.on_receive(line.strip())

        except Exception as e:
            if self.is_connected:
                self.is_connected = False
                logging.error(f"[RECEIVE ERROR] {e}")


class TCPProtocol(TCPHelpers):
    async def connect_tcp(self, ip, port):
        retry_delay = 3

        while True:
            try:
                logging.info(f"Connecting: {self.name} - {ip}:{port}")

                # Verifica IP antes (evita travar no DNS)
                try:
                    socket.inet_aton(ip)
                except OSError:
                    raise ValueError(f"Invalid IP address: {ip}")

                # Tenta abrir conexão com timeout real
                connect_task = asyncio.open_connection(ip, port)
                self.reader, self.writer = await asyncio.wait_for(connect_task, timeout=3)

                self.is_connected = True
                asyncio.create_task(events.on_connect(self.name))
                logging.info(f"✅ [CONNECTED] {self.name} - {ip}:{port}")

                # Cria tasks de leitura e monitoramento
                tasks = [
                    asyncio.create_task(self.receive_data_tcp()),
                    asyncio.create_task(self.monitor_connection()),
                ]

                # Espera até que uma delas finalize
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                # Cancela o resto
                for t in pending:
                    t.cancel()

                self.is_connected = False
                asyncio.create_task(events.on_disconnect(self.name))
                logging.info(f"🔌 [DISCONNECTED] {self.name} - Reconnecting...")

                retry_delay = 3  # reseta o delay após desconexão limpa

            except asyncio.TimeoutError:
                logging.warning(f"⏱️ [TIMEOUT] {self.name} - No response from {ip}:{port}")
            except ValueError as e:
                logging.error(f"❌ [INVALID IP] {self.name}: {e}")
                retry_delay = 10
            except OSError as e:
                logging.error(f"💥 [NETWORK ERROR] {self.name}: {e}")
                retry_delay = min(retry_delay * 2, 30)  # backoff até 30s
            except Exception as e:
                logging.error(f"❌ [UNEXPECTED ERROR] {self.name}: {e}")
                retry_delay = 5

            # Garante desconexão limpa
            if self.writer:
                try:
                    self.writer.close()
                    await self.writer.wait_closed()
                except Exception:
                    pass
                self.writer = None
                self.reader = None
                self.is_connected = False

            logging.info(f"🔁 Retrying {self.name} in {retry_delay}s...")
            await asyncio.sleep(retry_delay)

    async def write_tcp(self, data: str, verbose: bool=True):
        if self.is_connected and self.writer:
            try:
                data = data + "\n"
                self.writer.write(data.encode())
                await self.writer.drain()
                if verbose:
                    logging.info(f"[SENT] {data.strip()}")
            except Exception as e:
                logging.error(f"[SEND ERROR] {e}")
                if self.is_connected:
                    self.is_connected = False
                    asyncio.create_task(events.on_disconnect(self.name))
