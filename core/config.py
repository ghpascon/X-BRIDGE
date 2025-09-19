from dotenv import load_dotenv
import os


class Settings:
    def __init__(self):
        """Application settings loader and manager."""
        load_dotenv()
        self.data = {key: value for key, value in os.environ.items()}


settings = Settings()
