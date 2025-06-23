import asyncio
import json
import os

import aiohttp

import logging
from app.db.database import database_engine

from datetime import datetime
from app.models.rfid import DbEvent, DbTag


class RFIDAction:
    async def set_actions(self, data=None, action_path="config/actions.json"):
        if data is not None:
            self.actions = data
            os.makedirs(
                os.path.dirname(action_path), exist_ok=True
            )  # Garante que a pasta exista
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
        # DATABASE TAG
        asyncio.create_task(self.tag_db(tag))

        # POST TAG
        http_post = self.actions.get("HTTP_POST")
        if http_post:
            asyncio.create_task(self.post_tag(tag, http_post))

    async def tag_db(self, tag):
        try:
            time = datetime.now()
            async with database_engine.get_db() as db:
                current_tag = DbTag(
                    datetime=time,
                    device=tag.get("device"),
                    epc=tag.get("epc"),
                    tid=tag.get("tid"),
                    ant=tag.get("ant"),
                    rssi=tag.get("rssi"),
                )

                if current_tag.epc is None:
                    return
                db.add(current_tag)

                await db.commit()
        except Exception as e:
            logging.error(f"Erro ao salvar tag: {e}")

    async def post_tag(self, tag, endpoint):
        try:
            payload = {
                "event_type": "tag",
                "event_data": {"device": tag.get("device"), "data": tag},
            }            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload) as response:
                    pass
        except Exception as e:
            logging.info(f"Erro ao enviar tag: {e}")

    ### EVENTS
    async def on_events(self, device, event_type, event_data):
        # DATABASE EVENT
        asyncio.create_task(self.event_db(device, event_type, event_data))

        # POST EVENT
        http_post = self.actions.get("HTTP_POST")
        if http_post:
            asyncio.create_task(self.post_event(device, event_type, event_data, http_post))

    async def event_db(self, device, event_type, event_data):
        try:
            time = datetime.now()
            async with database_engine.get_db() as db:
                current_event = DbEvent(
                    datetime=time,
                    device=device,
                    event_type=event_type,
                    event_data=str(event_data)
                )

                db.add(current_event)

                await db.commit()
        except Exception as e:
            logging.error(f"Erro ao salvar evento: {e}")

    async def post_event(self, device, event_type, event_data, endpoint):
        try:
            payload = {
                "event_type": event_type,
                "event_data": {"device": device, "data": event_data},
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload) as response:
                    pass
        except Exception as e:
            logging.info(f"Erro ao enviar inventory: {e}")
