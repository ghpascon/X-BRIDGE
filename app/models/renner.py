"""
RFID models for SMARTX Connector.

Defines the Tag and Event models for storing RFID reader data
with proper indexing and relationships.
"""

from sqlalchemy import Column, Integer, String

from smartx_rfid.models import Base, BaseMixin


class Inventory(Base, BaseMixin):
	"""
	Inventory model for storing RFID tag read events.

	Stores information about RFID tags detected by readers,
	including EPC, TID, antenna, and signal strength data.
	"""

	__tablename__ = 'inventory'

	# Primary key
	id = Column(Integer, primary_key=True, autoincrement=True)

	sku = Column(String(100), nullable=False, index=True, unique=True)
	quantity = Column(Integer, nullable=False, index=False)
