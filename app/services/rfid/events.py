import logging
from smartx_rfid.utils import TagList


class Events:
	def __init__(self):
		self.tags = TagList()

	def on_event(self, name: str, event_type: str, event_data):
		"""
		Callback function to handle events.

		Args:
		        name: Name of the device
		        event_type: Type of event ('connection' or 'reading')
		        event_data: Data of the event
		"""
		if event_type == 'tag':
			self.on_tag(name=name, tag_data=event_data)
		else:
			logging.info(f'[ EVENT ] {name} - {event_type}: {event_data}')

	def on_tag(self, name: str, tag_data: dict):
		"""
		Callback function to handle tag read events.

		Args:
		        name: Name of the device
		        tag_data: Data of the read tag
		"""
		new_tag, tag = self.tags.add(tag_data, device=name)

		# NEW TAG
		if new_tag:
			logging.info(f'[ TAG ] {name} - Tag Data: {tag}')

		# EXISTING TAG
		elif tag is not None:
			pass
