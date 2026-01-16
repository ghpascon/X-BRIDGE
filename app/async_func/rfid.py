from app.services import rfid_manager
import logging
import asyncio
from app.core import settings
from datetime import datetime, timedelta
from app.models import get_all_models

async def connect_on_startup():
	"""Connect to RFID devices on application startup."""
	logging.info('Connecting to RFID devices on startup...')
	await rfid_manager.devices.connect_devices()

async def clear_old_tags():
	while True:
		if settings.CLEAR_OLD_TAGS_INTERVAL is None:
			await asyncio.sleep(60)
			continue
		await asyncio.sleep(settings.CLEAR_OLD_TAGS_INTERVAL)  
		if len(rfid_manager.events.tags) == 0:
			continue

		timestamp = datetime.now() - timedelta(seconds=settings.CLEAR_OLD_TAGS_INTERVAL)
		logging.info(f"Removing tags before {timestamp}")
		rfid_manager.events.tags.remove_tags_before_timestamp(timestamp)

		
async def clear_db():
	"""Clear database at startup and daily at midnight."""
	seconds_until_midnight = 0
	while True:
		# Sleep until midnight
		await asyncio.sleep(seconds_until_midnight)
		# Calculate initial seconds until midnight
		now = datetime.now()
		tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
		seconds_until_midnight = (tomorrow - now).total_seconds()
		
		logging.info(f"{'='*60}")
		logging.info("CLEAR DATABASE")

		# Validation
		if not isinstance(settings.STORAGE_DAYS, int):
			logging.warning("Invalid STORAGE_DAYS setting. Skipping database cleanup.")
			await asyncio.sleep(seconds_until_midnight)
			continue
		
		if rfid_manager.events.integration.db_manager is None:
			logging.warning("Database manager is not initialized. Skipping database cleanup.")
			await asyncio.sleep(seconds_until_midnight)
			continue

		logging.info(f"Clearing database entries older than {settings.STORAGE_DAYS} days.")
		
		# Calculate cutoff timestamp
		cutoff_date = datetime.now() - timedelta(days=settings.STORAGE_DAYS)
		
		# Get all models
		models = get_all_models()
		
		with rfid_manager.events.integration.db_manager.get_session() as session:
			for model in models:
				# Determine which timestamp column to use (prefer updated_at, fallback to created_at)
				timestamp_column = None
				if hasattr(model, 'updated_at'):
					timestamp_column = model.updated_at
				elif hasattr(model, 'created_at'):
					timestamp_column = model.created_at
				else:
					logging.info(f"Model {model.__tablename__} does not have 'updated_at' or 'created_at' column. Skipping.")
					continue
				
				try:
					# Delete old records
					deleted_count = session.query(model).filter(timestamp_column < cutoff_date).delete()
					session.commit()
					
					if deleted_count > 0:
						logging.info(f"Deleted {deleted_count} old records from {model.__tablename__}")
					else:
						logging.info(f"No old records to delete from {model.__tablename__}")
						
				except Exception as e:
					logging.error(f"Error clearing {model.__tablename__}: {e}")
					session.rollback()
		
		logging.info("Database cleanup completed.")
		logging.info(f"{'='*60}")
		



		