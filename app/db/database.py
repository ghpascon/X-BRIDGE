from app.db.session import Base, SessionLocal, sync_engine
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    async with SessionLocal() as db:
        yield db

if __name__ == "__main__":
    from app import models
    Base.metadata.create_all(bind=sync_engine)
