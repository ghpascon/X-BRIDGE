from app.schemas.tag import WriteTagValidator
import logging

class WriteCommands:
    async def write_epc(self, tag:dict):
        try:
            validated_tag = WriteTagValidator(**tag)
        except Exception as e:
            logging.warning(e)
            return  
        identifier = validated_tag.target_identifier
        value = validated_tag.target_value
        epc = validated_tag.new_epc
        password = validated_tag.password
        if identifier is None:
            self.write(f"#WRITE:{epc};{password}", False)
        else:              
            self.write(f"#WRITE:{epc};{password};{identifier};{value}", False)
