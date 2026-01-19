import json
import logging
import os


class Settings:
	def __init__(self, config_path='config/config.json'):
		"""Application settings loader and manager."""
		self._config_path = config_path
		self.load()

	def load(self):
		"""Load configuration from JSON file."""
		data = {}

		if os.path.exists(self._config_path):
			try:
				with open(self._config_path, 'r', encoding='utf8') as f:
					data = json.load(f)
			except Exception as e:
				logging.error(f'Error loading {self._config_path}: {e}')

		# Load variables with defaults
		self.TITLE = data.get('TITLE', 'SMARTX')
		self.LOG_PATH = data.get('LOG_PATH', 'Logs')
		self.STORAGE_DAYS = data.get('STORAGE_DAYS', 0)
		self.OPEN_BROWSER = data.get('OPEN_BROWSER', False)
		self.BEEP = data.get('BEEP', False)
		self.CLEAR_OLD_TAGS_INTERVAL = data.get('CLEAR_OLD_TAGS_INTERVAL', None)
		self.TAG_PREFIX = data.get('TAG_PREFIX', None)
		self.WEBHOOK_URL = data.get('WEBHOOK_URL', None)
		self.DATABASE_URL = data.get('DATABASE_URL', None)
		self.XTRACK_URL = data.get('XTRACK_URL', None)
		self.MQTT_URL = data.get('MQTT_URL', None)
		self.PORT = data.get('PORT', 5000)

	def save(self):
		"""Save all instance attributes except _config_path to JSON file."""
		try:
			logging.info(f'Saving config to: {self._config_path}')

			# Dynamically get all attributes except _config_path
			data = {key: value for key, value in self.__dict__.items() if key != '_config_path'}

			# Make sure folder exists
			os.makedirs(os.path.dirname(self._config_path), exist_ok=True)

			with open(self._config_path, 'w', encoding='utf8') as f:
				json.dump(data, f, indent=4, ensure_ascii=False)

		except Exception as e:
			logging.error(f'Error saving config: {e}')
