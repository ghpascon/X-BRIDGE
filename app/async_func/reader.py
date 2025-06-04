import asyncio
from app.db.database import get_db
from app.models.rfid import DbTag
from sqlalchemy import delete
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from app.schemas.devices import devices

async def connect_devices():
    tasks = []
    for name, device in devices.devices.items():
        try:
            print(f"🚀 Iniciando conexão para '{name}'")
            task = asyncio.create_task(device.connect())
            tasks.append(task)
        except Exception as e:
            print(f"❌ Erro ao iniciar conexão para '{name}': {e}")
    await asyncio.gather(*tasks)
    
async def daily_clear_db():
    while True:
        async with get_db() as db:
            limit_date = datetime.now(timezone.utc) - timedelta(days=settings.STORAGE_DAYS)
            limit_date = limit_date.replace(hour=0, minute=0, second=0, microsecond=0)
            stmt = delete(DbTag).where(DbTag.datetime < limit_date)
            await db.execute(stmt)
            await db.commit()
            print(f"Old tags deleted until {limit_date.isoformat()}")

        # Calcula a próxima meia-noite em horário de Brasília (UTC-3)
        now = datetime.now(timezone(timedelta(hours=-3)))
        next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait_seconds = (next_run - now).total_seconds()

        print(f"Next DB clear scheduled in {wait_seconds/3600:.2f} hours (Brasília time)")
        await asyncio.sleep(wait_seconds)