import asyncio
import json
import logging
import os
from datetime import datetime

import httpx

from app.core.config import settings
from app.core.indicator import beep
from app.db.database import database_engine
from app.models.rfid import DbEvent, DbTag


class Actions:
    async def get_actions_example(self, path="config/examples/actions.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return dict(json.load(f))
        except Exception as e:
            logging.error(f"[get_actions_example] Falha ao carregar '{path}': {e}")
            return None

    async def set_actions(self, data=None, action_path="config/actions.json"):
        if data is not None:
            self.actions = data
            os.makedirs(os.path.dirname(action_path), exist_ok=True)
            with open(action_path, "w") as f:
                json.dump(self.actions, f, indent=4)

        elif os.path.exists(action_path):
            with open(action_path, "r") as f:
                self.actions = json.load(f)
        else:
            self.actions = {}

        database_engine._initialize_engines_and_session()
        logging.info(f"[ Actions ] -> {self.actions}")

    ### TAG
    async def on_tag_events(self, tag):
        if self.actions.get("DATABASE_URL") is not None:
            asyncio.create_task(self.tag_db(tag))

        http_post = self.actions.get("HTTP_POST")
        if http_post:
            asyncio.create_task(self.post_tag(tag, http_post))

        xtrack_post = self.actions.get("XTRACK_URL")
        if xtrack_post:
            asyncio.create_task(self.post_tag_xtrack(tag, xtrack_post))

        if settings.data.get("BEEP", False):
            asyncio.create_task(beep())

    async def tag_db(self, tag):
        try:
            async with database_engine.get_db() as db:
                current_tag = DbTag(**tag)
                if current_tag.epc is None:
                    return
                db.add(current_tag)
                await db.commit()
        except Exception as e:
            logging.error(f"Erro ao salvar tag: {e}")

    async def post_tag(self, tag, endpoint):
        try:
            ts = tag.get("timestamp")
            if isinstance(ts, datetime):
                ts = ts.isoformat()
                tag["timestamp"] = ts

            payload = {
                "device": tag.get("device"),
                "event_type": "tag",
                "event_data": tag,
                "timestamp": ts,
            }
            async with httpx.AsyncClient() as client:
                await client.post(endpoint, json=payload, timeout=10.0)
        except Exception as e:
            logging.info(f"Erro ao enviar tag: {e}")

    async def post_tag_xtrack(self, tag, endpoint):
        try:
            payload = f"""<msg>
                        <command>ReportRead</command>
                        <data>EVENT=|DEVICENAME={tag.get("device", "")}|ANTENNANAME={tag.get("ant", "")}|TAGID={tag.get("epc", "")}|</data>
                        <cmpl>STATE=|DATA1=|DATA2=|DATA3=|DATA4=|DATA5=|</cmpl>
                        </msg>"""
            async with httpx.AsyncClient() as client:
                await client.post(
                    endpoint,
                    content=payload,
                    headers={"Content-Type": "application/xml"},
                    timeout=10.0,
                )
        except Exception as e:
            logging.info(f"Erro ao enviar tag: {e}")

    ### EVENTS
    async def on_events(self, device, event_type, event_data, timestamp):
        self.events.appendleft(
            {
                "timestamp": timestamp,
                "device": device,
                "event_type": event_type,
                "event_data": event_data,
            }
        )

        if self.actions.get("DATABASE_URL") is not None:
            asyncio.create_task(self.event_db(device, event_type, event_data, timestamp))

        http_post = self.actions.get("HTTP_POST")
        if http_post:
            asyncio.create_task(
                self.post_event(device, event_type, event_data, timestamp, http_post)
            )

    async def event_db(self, device, event_type, event_data, timestamp):
        try:
            async with database_engine.get_db() as db:
                current_event = DbEvent(
                    timestamp=timestamp,
                    device=device,
                    event_type=event_type,
                    event_data=str(event_data),
                )
                db.add(current_event)
                await db.commit()
        except Exception as e:
            logging.error(f"Erro ao salvar evento: {e}")

    async def post_event(self, device, event_type, event_data, timestamp, endpoint):
        try:
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()

            payload = {
                "timestamp": timestamp,
                "device": device,
                "event_type": event_type,
                "event_data": event_data,
            }
            async with httpx.AsyncClient() as client:
                await client.post(endpoint, json=payload, timeout=10.0)
        except Exception as e:
            logging.info(f"Erro ao enviar inventory: {e}")
