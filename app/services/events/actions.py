import asyncio
import json
import logging
import os
from datetime import datetime
from urllib.parse import urlparse

import httpx
from gmqtt import Client as MQTTClient

from app.core import settings
from app.core.indicator import beep
from app.db.database import database_engine
from app.models.rfid import DbEvent, DbTag


class Actions:
    # -------------------------------
    # CONFIG ACTIONS
    # -------------------------------
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

    # -------------------------------
    # TAG HANDLING
    # -------------------------------
    async def on_tag_events(self, tag):
        if self.actions.get("DATABASE_URL"):
            asyncio.create_task(self.tag_db(tag))

        http_post = self.actions.get("HTTP_POST")
        mqtt_url = self.actions.get("MQTT_URL")
        xtrack_post = self.actions.get("XTRACK_URL")
        payload = {
            "timestamp": datetime.now().isoformat(),
            "device": tag.get("device", ""),
            "event_type": "tag",
            "event_data": tag,
        }

        if http_post:
            asyncio.create_task(self.send_payload(payload, http_post))
        if mqtt_url:
            asyncio.create_task(self.send_payload(payload, mqtt_url, mqtt=True))
        if xtrack_post:
            asyncio.create_task(self.post_tag_xtrack(tag, xtrack_post))

        if settings.data.get("BEEP", False):
            asyncio.create_task(beep())

    async def tag_db(self, tag):
        try:
            async with database_engine.get_db() as db:
                # Use safe method to handle extra fields like 'count'
                current_tag = DbTag.create_from_dict(tag)
                if current_tag.epc is None:
                    return
                db.add(current_tag)
                await db.commit()
        except Exception as e:
            logging.error(f"Erro ao salvar tag: {e}")

    # -------------------------------
    # EVENTS HANDLING
    # -------------------------------
    async def on_events(self, device, event_type, event_data, timestamp):
        self.events.appendleft(
            {
                "timestamp": timestamp,
                "device": device,
                "event_type": event_type,
                "event_data": event_data,
            }
        )

        # Save to database if configured
        if self.actions.get("DATABASE_URL"):
            asyncio.create_task(self.event_db(device, event_type, event_data, timestamp))

        payload = {
            "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
            "device": device,
            "event_type": event_type,
            "event_data": event_data,
        }

        # HTTP POST
        http_post = self.actions.get("HTTP_POST")
        if http_post:
            asyncio.create_task(self.send_payload(payload, http_post))

        # MQTT POST
        mqtt_url = self.actions.get("MQTT_URL")
        if mqtt_url:
            asyncio.create_task(self.send_payload(payload, mqtt_url, mqtt=True))

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

    # -------------------------------
    # GENERIC SENDER (HTTP POST / MQTT)
    # -------------------------------
    mqtt_client = None  # persistent client
    mqtt_connected = asyncio.Event()  # event to wait until connected

    async def init_mqtt(self, endpoint):
        if self.mqtt_client is not None:
            return  # already initialized

        parsed = urlparse(endpoint)
        broker = parsed.hostname
        port = parsed.port or 1883

        self.mqtt_client = MQTTClient("client_id")

        # optional: define on_connect and on_disconnect callbacks
        self.mqtt_client.on_connect = (
            lambda client, flags, rc, properties: self.mqtt_connected.set()
        )
        self.mqtt_client.on_disconnect = (
            lambda client, packet, exc=None: self.mqtt_connected.clear()
        )

        await self.mqtt_client.connect(broker, port)
        await self.mqtt_connected.wait()  # ensure connection before publishing

    def convert_datetimes(self, obj):
        """Converte qualquer datetime em string ISO dentro de dicionários aninhados."""
        if isinstance(obj, dict):
            return {k: self.convert_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_datetimes(v) for v in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    async def send_payload(self, payload, endpoint, mqtt=False):
        try:
            payload = self.convert_datetimes(payload)
            ts = payload.get("timestamp")
            if isinstance(ts, datetime):
                payload["timestamp"] = ts.isoformat()

            if mqtt:
                await self.init_mqtt(endpoint)
                parsed = urlparse(endpoint)
                topic = parsed.path.lstrip("/")
                self.mqtt_client.publish(topic, json.dumps(payload))
                logging.info(f"Payload published to MQTT {topic}")
            else:
                async with httpx.AsyncClient() as client:
                    await client.post(endpoint, json=payload, timeout=10.0)
                    logging.info(f"Payload posted to HTTP {endpoint}")

        except Exception as e:
            logging.info(f"Erro ao enviar payload: {e}")

    # -------------------------------
    # XTRACK POST
    # -------------------------------
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
