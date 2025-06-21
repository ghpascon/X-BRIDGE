import asyncio
import json

import aiohttp

import logging


class ReaderHelpers:
    async def configure_interface(self, session):
        return await self.post_to_reader(
            session,
            self.endpoint_interface,
            payload=self.interface_config,
            method="put",
        )

    async def stop_inventory(self, session=None):
        print(f"STOP -> {self.config.get('NAME')}")
        return await self.post_to_reader(session, self.endpoint_stop)

    async def start_inventory(self, session=None):
        print(f"START -> {self.config.get('NAME')}")
        return await self.post_to_reader(
            session, self.endpoint_start, payload=self.config.get("READING_CONFIG")
        )

    async def post_to_reader(
        self, session, endpoint, payload=None, method="post", timeout=3
    ):
        try:
            if session is None:
                async with aiohttp.ClientSession(
                    auth=self.auth, connector=aiohttp.TCPConnector(ssl=False)
                ) as session:
                    await self.post_to_reader(
                        session, endpoint, payload, method, timeout
                    )
                    return
            if method == "post":
                async with session.post(
                    endpoint, json=payload, timeout=timeout
                ) as response:
                    print(f"{endpoint} -> {response.status}")
                    return response.status == 204
            elif method == "put":
                async with session.put(
                    endpoint, json=payload, timeout=timeout
                ) as response:
                    print(f"{endpoint} -> {response.status}")
                    return response.status == 204
        except Exception as e:
            logging.error(f"Error posting to {endpoint}: {e}")
            return False

    async def get_tag_list(self, session):
        try:
            async with session.get(self.endpointDataStream, timeout=None) as response:
                if response.status != 200:
                    print(f"Failed to connect to data stream: {response.status}")
                    return
                print("Searching for tags...")
                print("EPCs of tags detected in field of view:")

                async for line in response.content:
                    try:
                        string = line.decode("utf-8").strip()
                        if not string:
                            continue
                        jsonEvent = json.loads(string)

                        if "inventoryStatusEvent" in jsonEvent:
                            status = jsonEvent["inventoryStatusEvent"][
                                "inventoryStatus"
                            ]
                            if status == "running":
                                asyncio.create_task(self.on_start())
                            else:
                                asyncio.create_task(self.on_stop())
                        elif "tagInventoryEvent" in jsonEvent:
                            tagEvent = jsonEvent["tagInventoryEvent"]
                            asyncio.create_task(self.on_tag(tagEvent))

                    except (json.JSONDecodeError, UnicodeDecodeError) as parse_error:
                        logging.error(f"Warning: Failed to parse event: {parse_error}")
                    except Exception as e:
                        logging.error(f"Unexpected error: {e}")

        except aiohttp.ClientError as e:
            logging.error(f"Connection error: {e}")

    async def get_tid_from_epc(self, epc):
        current_tags = list(self.tags)
        for tag in current_tags:
            if tag == epc:
                return self.tags.get(tag).get("tid")
        return None

    async def get_gpo_command(self, i=1, state="low", control="static", time=1000):
        if control == "static":
            gpo_command = {
                "gpoConfigurations": [{"gpo": i, "state": state, "control": control}]
            }

        elif control == "pulsed":
            gpo_command = {
                "gpoConfigurations": [
                    {
                        "gpo": i,
                        "state": state,
                        "pulseDurationMilliseconds": time,
                        "control": control,
                    }
                ]
            }

        return gpo_command
