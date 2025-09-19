import os

from dotenv import load_dotenv


class Settings:
    def __init__(self):
        """Application settings loader and manager."""
        load_dotenv()
        self.data = {key: value for key, value in os.environ.items()}


settings = Settings()
