class AddDevice:
    def __init__(self):
        self.devices = {}

    def _generate_unique_name(self, base_name):
        if base_name not in self.devices:
            return base_name
        
        index = 2
        new_name = f"{base_name}_{index}"
        while new_name in self.devices:
            index += 1
            new_name = f"{base_name}_{index}"
        return new_name

    def add_device(self, data):
        reader = data.get("READER")
        name = data.get("NAME", "UNKNOWN")

        # Garante nome único
        unique_name = self._generate_unique_name(name)

        print(f"🔍 Adicionando dispositivo: {unique_name}")
        print(f"📡 Tipo de leitor: {reader}")

        if reader == "R700":
            from ..readers.R700 import R700
            self.devices[unique_name] = R700(data)
        elif reader == "UR4":
            from ..readers.UR4 import UR4
            self.devices[unique_name] = UR4(data)
        else:
            print(f"⚠️ Leitor '{reader}' não reconhecido. Dispositivo '{unique_name}' não adicionado.")
        
        print(f"✅ Dispositivo '{unique_name}' adicionado com sucesso.")

    def get_device_list(self):
        return [device for device in self.devices]
