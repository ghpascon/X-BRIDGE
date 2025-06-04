from ..validators.tag import TagSchema
from pydantic import ValidationError
from ..logger import log_error

class RFID:
    def __init__(self):
        self.tags = {}

    async def clear_tags(self, reader: str | None):
        if reader is None:
            self.tags = {}
            return
        self.tags = {
            k: v for k, v in self.tags.items() if v.get("device") != reader
        }
        
    async def on_tag(self, tag: dict, verbose = True):
        try:
            tag_validado = TagSchema(**tag)

            tag_exist = False
            if tag_validado.epc in self.tags:
                tag_exist = True

            if tag_exist and tag_validado.rssi <= self.tags[tag_validado.epc].get("rssi"):
                return

            current_tag = {
                "device":tag_validado.device,
                "epc":tag_validado.epc,
                "tid":tag_validado.tid,
                "ant":tag_validado.ant,
                "rssi":tag_validado.rssi,
            }
            if verbose and not tag_exist:
                print(f"[TAG] {current_tag}")
            self.tags[tag_validado.epc] = current_tag

        except ValidationError as e:
            log_error(f"❌ Tag inválida: {e.json()}")

rfid = RFID()