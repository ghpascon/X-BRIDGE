import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pyepc import SGTIN

from app.core.path import get_prefix_from_path
from app.schemas.devices import BooleanDeviceRequest
from app.schemas.events import EventRequest
from app.schemas.responses import rfid_base_responses
from app.schemas.tag import TagGtinSimulator, TagListSimulator, TagRequestSimulator
from app.services.events import events

router_prefix = get_prefix_from_path(__file__)
router = APIRouter(prefix=router_prefix, tags=[router_prefix])


@router.post(
    "/tag",
    responses=rfid_base_responses,
    summary="Simulate RFID tag read",
    description="Simulates an RFID tag being read and sends the data to the tag processing logic.",
)
async def simulator_tag(tag: TagRequestSimulator):
    try:
        await events.on_tag(tag.model_dump())
        return {"msg": "success"}
    except Exception as e:
        logging.error(f"Error while processing tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tag_list",
    summary="Simulate RFID sequential tag list",
    description="Simulates an RFID tag list being read and sends the data to the tag processing logic.",
)
async def tag_list(tag_generator: TagListSimulator):
    start_epc = tag_generator.start_epc
    qtd = tag_generator.qtd

    try:
        base_value = int(start_epc, 16)
    except ValueError:
        return JSONResponse(
            content={"error": "EPC inválido, deve ser apenas hexadecimal"}, status_code=400
        )

    for i in range(qtd):
        epc_value = base_value + i
        epc_hex = f"{epc_value:024x}"
        await events.on_tag(
            {
                "device": tag_generator.device,
                "epc": epc_hex,
                "tid": None,
            }
        )

    return JSONResponse(content={"detail": f"{qtd} tags ok"})


@router.post(
    "/gtin_list",
    summary="Simulate RFID tags from GTIN",
    description="Generates and simulates RFID tags based on a GTIN (14 digits) and creates sequential EPCs using SGTIN encoding.",
)
async def gtin_list(tag_generator: TagGtinSimulator):
    gtin = tag_generator.gtin
    qtd = tag_generator.qtd
    start_serial = tag_generator.start_serial
    device = tag_generator.device

    # --- GTIN-14 Validation -------------------------------
    def validate_gtin14(gtin_str: str) -> bool:
        """Validate GTIN-14 check digit using standard algorithm"""
        if len(gtin_str) != 14 or not gtin_str.isdigit():
            return False

        digits = [int(d) for d in gtin_str]
        check_digit = digits[-1]
        body = digits[:-1]

        # Weights 3 and 1 from right to left
        weights = [3 if (i % 2 == 0) else 1 for i in range(len(body) - 1, -1, -1)]

        total = sum(d * w for d, w in zip(body, weights))
        calc_digit = (10 - (total % 10)) % 10

        return calc_digit == check_digit

    # Validation check
    if not validate_gtin14(gtin):
        raise HTTPException(
            status_code=400,
            detail=f"GTIN {gtin} is invalid. Must contain 14 digits and pass check digit validation.",
        )

    # -------------------------------------------------------

    try:
        # Generate sequential tags from GTIN
        for i in range(qtd):
            # Create SGTIN from GTIN and sequential serial number
            sgtin = SGTIN.from_sgtin(
                gtin=gtin,
                serial_number=str(start_serial + i),
                company_prefix_len=7,  # Standard 7-digit company prefix
            )
            # Encode to hexadecimal EPC
            epc_hex = sgtin.encode().lower()

            # Send tag to processing pipeline
            await events.on_tag(
                {
                    "device": device,
                    "epc": epc_hex,
                    "tid": None,
                }
            )

        return JSONResponse(content={"detail": f"{qtd} tags generated from GTIN {gtin}."})

    except Exception as e:
        logging.error(f"Error while processing GTIN tag generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/connection",
    responses=rfid_base_responses,
    summary="Simulate connection state",
    description="Simulates the connection state change for the specified device.",
)
async def simulator_connection(connection: BooleanDeviceRequest):
    try:
        if connection.state:
            await events.on_connect(connection.device)
            return {"msg": f"{connection.device} CONNECTED"}
        else:
            await events.on_disconnect(connection.device)
            return {"msg": f"{connection.device} DISCONNECTED"}
    except Exception as e:
        logging.error(f"Error while processing connection simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/inventory",
    responses=rfid_base_responses,
    summary="Simulate inventory state",
    description="Starts or stops the inventory simulation for the specified device.",
)
async def simulator_inventory(inventory: BooleanDeviceRequest):
    try:
        if inventory.state:
            await events.on_start(inventory.device)
            return {"msg": f"{inventory.device} STARTED"}
        else:
            await events.on_stop(inventory.device)
            return {"msg": f"{inventory.device} STOPPED"}
    except Exception as e:
        logging.error(f"Error while processing inventory simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/event",
    responses=rfid_base_responses,
    summary="Simulate an event",
    description="Simulate an event with a simulated data",
)
async def simulator_event(event: EventRequest):
    try:
        event_json = event.model_dump()
        await events.on_event(**event_json)
        return {"msg": f"Received event: {event_json}"}
    except Exception as e:
        logging.error(f"Error while processing event simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
