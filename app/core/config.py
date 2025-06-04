import json

class Settings:
    def __init__(self):
        with open("config/config.json") as f:
            config = json.load(f)
        for key, value in config.items():
            setattr(self, key, value)

settings = Settings()

