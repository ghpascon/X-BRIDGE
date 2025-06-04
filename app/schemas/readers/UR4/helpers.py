from app.schemas.logger import log_error,log_info
import asyncio

class ReaderHelpers:
    async def monitor_connection(self):
        while self.is_connected:
            await asyncio.sleep(1)
            if self.writer.is_closing():
                self.is_connected = False
                log_info("[DESCONECTADO] Socket fechado.")
                break

    async def receive_data(self):
        await asyncio.sleep(0.03)
        buffer = b''
        try:
            while True:
                data = await self.reader.read(1024)
                if not data:
                    raise ConnectionError("Conexão perdida")
                buffer += data

                # Processa pacotes completos com prefixo a5 5a e sufixo 0d 0a
                while True:
                    start = buffer.find(b'\xa5\x5a')
                    end = buffer.find(b'\x0d\x0a', start)
                    if start != -1 and end != -1 and end > start:
                        packet = buffer[start:end + 2]
                        buffer = buffer[end + 2:]
                        await self.on_received_cmd(packet)
                    else:
                        break

        except Exception as e:
            self.is_connected = False
            log_error(f"[ERRO RECEBIMENTO] {e}")

    async def get_temperature(self):
        while True:
            await asyncio.sleep(10)
            if not self.setup:continue
            await self.send_data([0xa5, 0x5a, 0x00, 0x08, 0x34, 0x00, 0x0d, 0x0a])

    async def decode_temperature(self, response_bytes):
        temperature = int(int((response_bytes[6] << 8) | response_bytes[7]) / 100)
        log_info(f"TEMPERATURE: {temperature}")
        return temperature
    
    async def get_gpi_state(self):
        while True:
            await asyncio.sleep(0.1)
            if not self.setup:continue
            await self.send_data([0xa5, 0x5a, 0x00, 0x09, 0xa1, 0x0a, 0x00, 0x0d, 0x0a],False)
            
    async def ensure_reading_command(self):
        while True:
            await asyncio.sleep(1)
            if self.is_reading: 
                await self.send_data([0xa5, 0x5a, 0x00, 0x0a, 0x82, 0x00, 0x00, 0x00, 0x0d, 0x0a], False)
                
                continue
            await self.send_data([0xa5, 0x5a, 0x00, 0x08, 0x8c, 0x00, 0x0d, 0x0a], False)
            await self.send_data([0xa5, 0x5a, 0x00, 0x09, 0x8d, 0x01, 0x00, 0x0d, 0x0a], False)                

    async def get_tid_from_epc(self, epc):
        current_tags = list(self.tags) 
        for tag in current_tags:
            if tag == epc:
                return self.tags.get(tag).get('tid')
        return None
    
    async def get_bcc(self, data):
        bcc = 0
        for byte in data[2:-3]:
            bcc ^= byte
        return bcc