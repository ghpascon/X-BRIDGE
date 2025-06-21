import os
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .session import Base
from app.models.rfid import DbTag
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete
from app import models  # Garante que os modelos estejam importados
import logging
from sqlalchemy.orm import DeclarativeMeta
import csv
import zipfile
from io import StringIO, BytesIO

from fastapi import Response
from fastapi.responses import StreamingResponse
from sqlalchemy.future import select


class DatabaseEngine:
    def __init__(self):
        self.database_url = None
        self.sync_url = None
        self.sync_engine = None
        self.async_engine = None
        self.SessionLocal = None

        result = self._initialize_engines_and_session()
        if isinstance(result, dict) and "error" in result:
            logging.error(
                f"[DatabaseEngine.__init__] Erro ao inicializar: {result['error']}"
            )

    def _load_database_url(self, path="config/actions.json"):
        try:
            if not os.path.exists(path):
                logging.error(
                    f"[DatabaseEngine._load_database_url] Arquivo de configuração não encontrado: {path}"
                )
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            url = data.get("DATABASE_URL")
            if not url:
                logging.error(
                    f"[DatabaseEngine._load_database_url] 'DATABASE_URL' não encontrada no arquivo: {path}"
                )
                return None
            return url
        except json.JSONDecodeError as e:
            logging.error(
                f"[DatabaseEngine._load_database_url] Erro ao decodificar JSON do arquivo {path}: {e}"
            )
            return None
        except Exception as e:
            logging.error(
                f"[DatabaseEngine._load_database_url] Erro inesperado ao carregar DATABASE_URL: {e}"
            )
            return None

    def _initialize_engines_and_session(self):
        try:
            self.database_url = self._load_database_url()
            if not self.database_url:
                msg = "URL do banco de dados inválida ou não encontrada. Inicialização adiada."
                logging.error(f"[DatabaseEngine._initialize_engines_and_session] {msg}")
                # Deixa atributos None e retorna erro
                return {"error": msg}

            dialect_plus_driver = self.database_url.split("://")[0]
            if "+" in dialect_plus_driver:
                dialect, async_driver = dialect_plus_driver.split("+")
            else:
                dialect = dialect_plus_driver
                async_driver = None

            default_sync_driver = {
                "mysql": "pymysql",
                "postgresql": "psycopg2",
                "sqlite": None,
            }.get(dialect, None)

            if default_sync_driver:
                self.sync_url = self.database_url.replace(
                    f"+{async_driver}", f"+{default_sync_driver}"
                )
            else:
                self.sync_url = self.database_url.replace(f"+{async_driver}", "")

            self.sync_engine = create_engine(self.sync_url, echo=False)
            self.async_engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
            )

            self.SessionLocal = sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
            )

            self.create_tables()
            logging.info(
                "[DatabaseEngine._initialize_engines_and_session] Inicialização das engines e sessão realizada com sucesso."
            )
            return True
        except Exception as e:
            logging.error(
                f"[DatabaseEngine._initialize_engines_and_session] Erro ao inicializar engines e sessão: {e}"
            )
            self.database_url = None
            self.sync_url = None
            self.sync_engine = None
            self.async_engine = None
            self.SessionLocal = None
            return {"error": str(e)}

    def create_tables(self):
        if self.sync_engine is None:
            logging.error(
                "[DatabaseEngine.create_tables] sync_engine não inicializada. Ignorando criação de tabelas."
            )
            return
        try:
            Base.metadata.create_all(bind=self.sync_engine)
            logging.info("[DatabaseEngine.create_tables] Tabelas criadas ou já existentes.")
        except Exception as e:
            logging.error(f"[DatabaseEngine.create_tables] Erro ao criar tabelas: {e}")
            # NÃO levanta exceção

    def reload_database_url(self, new_url: str):
        try:
            self.database_url = new_url
            result = self._initialize_engines_and_session()
            if result is True:
                logging.info(
                    "[DatabaseEngine.reload_database_url] URL do banco de dados recarregada com sucesso."
                )
                return True
            else:
                # result contém o dict {"error": ...}
                logging.error(f"[DatabaseEngine.reload_database_url] {result['error']}")
                return result
        except Exception as e:
            logging.error(
                f"[DatabaseEngine.reload_database_url] Erro ao recarregar DATABASE_URL: {e}"
            )
            return {"error": str(e)}

    @asynccontextmanager
    async def get_db(self):
        if self.SessionLocal is None:
            logging.error(
                "[DatabaseEngine.get_db] Sessão não inicializada, não é possível obter conexão com o banco."
            )
            yield None
            return
        try:
            async with self.SessionLocal() as db:
                yield db
        except Exception as e:
            logging.error(
                f"[DatabaseEngine.get_db] Erro ao obter sessão do banco de dados: {e}"
            )
            yield None

    async def clear_db(self, days):
        if self.SessionLocal is None:
            logging.error(
                "[DatabaseEngine.clear_db] Session not initialized, operation ignored."
            )
            return {"error": "Session not initialized"}

        try:
            async with self.get_db() as db:
                if db is None:
                    logging.error(
                        "[DatabaseEngine.clear_db] Session returned None, operation aborted."
                    )
                    return {"error": "Session returned None"}

                limit_date = datetime.now(timezone.utc) - timedelta(days=days)
                limit_date = limit_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

                deleted_tables = []

                for cls in Base.__subclasses__():
                    if isinstance(cls, DeclarativeMeta) and hasattr(cls, "datetime"):
                        try:
                            stmt = delete(cls).where(cls.datetime < limit_date)
                            await db.execute(stmt)
                            deleted_tables.append(cls.__tablename__)
                        except Exception as table_exc:
                            logging.error(
                                f"[DatabaseEngine.clear_db] Failed to clear table '{cls.__tablename__}': {table_exc}"
                            )

                await db.commit()
                logging.info(
                    f"[DatabaseEngine.clear_db] Old records deleted up to {limit_date.isoformat()} from tables: {deleted_tables}"
                )
                return {"success": True, "deleted_tables": deleted_tables}

        except Exception as e:
            logging.error(f"[DatabaseEngine.clear_db] Error while clearing database: {e}")
            return {"error": str(e)}

    async def get_report(self):
        try:
            async with self.get_db() as db:
                if db is None:
                    logging.error("[get_report] Database session not available")
                    return Response(
                        content="Database session unavailable", status_code=503
                    )

                zip_buffer = BytesIO()
                table_count = 0
                exported_tables = []

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for cls in Base.__subclasses__():
                        if isinstance(cls, DeclarativeMeta):
                            table_name = getattr(cls, "__tablename__", cls.__name__)
                            try:
                                logging.info(f"[get_report] Processing table: {table_name}")
                                result = await db.execute(select(cls))
                                rows = result.scalars().all()

                                csv_buffer = StringIO()
                                writer = csv.writer(csv_buffer)

                                # Header
                                headers = [col.name for col in cls.__table__.columns]
                                writer.writerow(headers)

                                # Data rows
                                for row in rows:
                                    writer.writerow(
                                        [
                                            getattr(row, col.name)
                                            for col in cls.__table__.columns
                                        ]
                                    )

                                csv_buffer.seek(0)
                                zip_file.writestr(
                                    f"{table_name}.csv", csv_buffer.read()
                                )
                                logging.info(
                                    f"[get_report] Exported {len(rows)} rows from table: {table_name}"
                                )
                                table_count += 1
                                exported_tables.append(table_name)

                            except Exception as table_error:
                                logging.error(
                                    f"[get_report] Failed to export table {table_name}: {table_error}"
                                )

                if table_count == 0:
                    logging.info("[get_report] No tables were exported. ZIP will be empty.")

                zip_buffer.seek(0)
                logging.info(
                    f"[get_report] Report generation completed. {table_count} tables exported: {exported_tables}"
                )

                return StreamingResponse(
                    zip_buffer,
                    media_type="application/zip",
                    headers={"Content-Disposition": "attachment; filename=report.zip"},
                )

        except Exception as e:
            logging.error(f"[get_report] Failed to generate reports: {e}")
            return Response(content=f"Failed to get reports: {str(e)}", status_code=500)


database_engine = DatabaseEngine()
