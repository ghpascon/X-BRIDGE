class AddDevice:
    def __init__(self):
        self.devices = {}

    def add_device(self, data, name="default"):
        reader = data.get("READER")

        # Ensure unique device name
        unique_name = self._generate_unique_name(name)

        print(f"🔍 Adding device: {unique_name}")
        print(f"📡 Reader type: {reader}")

        ### R700
        if reader == "R700_IOT":
            from ..readers.RFID.R700_IOT import R700_IOT

            self.devices[unique_name] = R700_IOT(data, name)

        ### UR4
        elif reader == "UR4":
            from ..readers.RFID.UR4 import UR4

            self.devices[unique_name] = UR4(data, name)

        ### X714
        elif reader == "X714":
            from ..readers.RFID.X714 import X714

            self.devices[unique_name] = X714(data, name)

        ### ICARD
        elif reader == "ICARD":
            from ..readers.RFID.ICARD import ICARD

            self.devices[unique_name] = ICARD(data, name)

        ### SERIAL
        elif reader == "SERIAL":
            from ..readers.OTHERS.SERIAL import SERIAL

            self.devices[unique_name] = SERIAL(data, name)

        ### TCP
        elif reader == "TCP":
            from ..readers.OTHERS.TCP import TCP

            self.devices[unique_name] = TCP(data, name)

        ###
        else:
            print(f"⚠️ Unknown reader type '{reader}'. Device '{unique_name}' was not added.")
            return  # Exit early if device is invalid

        print(f"✅ Device '{unique_name}' added successfully.")

    def get_device_list(self):
        return list(self.devices.keys())

    def is_rfid_reader(self, device):
        try:
            return self.devices.get(device).is_rfid_reader
        except:
            return False

    def _generate_unique_name(self, base_name):
        name = base_name
        count = 1
        while name in self.devices:
            name = f"{base_name}_{count}"
            count += 1
        return name
