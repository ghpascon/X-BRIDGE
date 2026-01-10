import logging


class AddDevice:
    def __init__(self):
        self.devices = {}

    def add_device(self, data, name="default"):
        """Adiciona um device ao sistema com validação e tratamento de erros robusto."""
        reader = data.get("READER")

        if not reader:
            logging.error(f"❌ Configuração inválida para device '{name}': READER não especificado")
            return False

        # Ensure unique device name
        unique_name = self._generate_unique_name(name)

        logging.info(f"🔍 Adding device: {unique_name}")
        logging.info(f"📡 Reader type: {reader}")

        try:
            ### R700
            if reader == "R700_IOT":
                from .drivers.RFID.R700_IOT import R700_IOT

                self.devices[unique_name] = R700_IOT(data, unique_name)

            ### UR4
            elif reader == "UR4":
                from .drivers.RFID.UR4 import UR4

                self.devices[unique_name] = UR4(data, unique_name)

            ### X714
            elif reader == "X714":
                from .drivers.RFID.X714 import X714

                self.devices[unique_name] = X714(data, unique_name)

            ### ICARD
            elif reader == "ICARD":
                from .drivers.RFID.ICARD import ICARD

                self.devices[unique_name] = ICARD(data, unique_name)

            ### SERIAL
            elif reader == "SERIAL":
                from .drivers.OTHERS.SERIAL import SERIAL

                self.devices[unique_name] = SERIAL(data, unique_name)

            ### TCP
            elif reader == "TCP":
                from .drivers.OTHERS.TCP import TCP

                self.devices[unique_name] = TCP(data, unique_name)

            ###
            else:
                logging.warning(
                    f"⚠️ Unknown reader type '{reader}'. Device '{unique_name}' was not added."
                )
                return False  # Exit early if device is invalid

            logging.info(f"✅ Device '{unique_name}' added successfully.")
            return True

        except Exception as e:
            logging.error(f"❌ Erro ao criar device '{unique_name}' do tipo '{reader}': {e}")
            # Remove o device se foi parcialmente criado
            if unique_name in self.devices:
                del self.devices[unique_name]
            return False

    def get_device_list(self):
        return list(self.devices.keys())

    def is_rfid_reader(self, device):
        try:
            return self.devices.get(device).is_rfid_reader
        except Exception:
            return False

    def _generate_unique_name(self, base_name):
        name = base_name
        count = 1
        while name in self.devices:
            name = f"{base_name}_{count}"
            count += 1
        return name
