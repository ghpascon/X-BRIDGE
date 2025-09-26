import json
import logging
import re
from typing import Any, Optional, Tuple

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from ..devices import devices


def validate_device(device: str, need_connected: bool = True) -> Tuple[bool, str | dict]:
    """
    Validate if the device exists and optionally if it is connected.
    """
    if device not in devices.get_device_list():
        return False, "Invalid Device"

    if not devices.devices.get(device).is_connected and need_connected:
        return False, "Device is not connected"

    return True, {"msg": "success"}


def load_example_from_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.info(f"Erro ao carregar JSON de exemplo: {e}")
        return {}


class TagRequest(BaseModel):
    device: str = Field(default="DEVICE_01")
    epc: str = Field(default="000000000000000000000001")
    tid: Optional[str] = Field(default="000000000000000000000002")
    ant: Optional[int] = Field(default=1)
    rssi: Optional[int] = Field(default=-80)

    @field_validator("epc", "tid")
    def validate_epc_length_and_hex(cls, v, info):
        if v is None:
            return v
        if len(v) != 24:
            raise ValueError(f"{info.field_name} must have exactly 24 characters")
        if not re.fullmatch(r"[0-9a-fA-F]{24}", v):
            raise ValueError(
                f"{info.field_name} must contain only hexadecimal characters (0-9, a-f)"
            )
        return v.lower()

    @field_validator("rssi")
    def validate_rssi(cls, v):
        if v is None:
            return -80
        if not isinstance(v, int):
            raise ValueError("rssi must be an integer")
        return -abs(v)  # força negativo

    @field_validator("ant")
    def validate_ant(cls, v):
        return v if v is not None else 1


class TagRequestSimulator(BaseModel):
    device: Optional[str] = Field("DEVICE_01")
    epc: str = Field("000000000000000000000001")
    tid: Optional[str] = Field("000000000000000000000002")
    ant: int = Field(1)
    rssi: int = Field(-80)

    @field_validator("epc", "tid")
    def validate_epc_length_and_hex(cls, v, info: ValidationInfo):
        if v is None:
            return v
        if len(v) != 24:
            raise ValueError(f"{info.field_name} must have exactly 24 characters")
        if not re.fullmatch(r"[0-9a-fA-F]{24}", v):
            raise ValueError(
                f"{info.field_name} must contain only hexadecimal characters (0-9, a-f)"
            )
        return v


class ActionsRequest(BaseModel):
    HTTP_POST: Optional[str] = Field("http://localhost:5001")
    DATABASE_URL: Optional[str] = Field(
        "mysql+aiomysql://root:admin@localhost:3306/middleware_smartx"
    )
    MQTT_URL: Optional[str] = Field(
        "mqtt://localhost:1883/connector"
    ) 

    XTRACK_URL: Optional[str] = Field("https://192.168.0.100:6100/req")
    STORAGE_DAYS: int = Field(0)
    LOG_PATH: str = Field("Logs")


class BooleanDeviceRequest(BaseModel):
    device: str = Field("DEVICE01")
    state: bool = True


class EventRequest(BaseModel):
    device: str = Field("DEVICE01")
    event_type: str = Field("event_type")
    event_data: Any = {"data": "xyz"}


class SetGpoRequest(BaseModel):
    device: str = Field("DEVICE01")
    pin: Optional[int] = Field(1)
    state: Optional[bool] = Field(True)
    control: Optional[str] = Field("static")
    time: Optional[int] = Field(1000)


class TagListSimulator(BaseModel):
    device: str = Field("DEVICE01")
    start_epc: str = Field("000000000000000000000001")
    qtd: int = 50

    @field_validator("start_epc")
    def validate_epc_length_and_hex(cls, v, info: ValidationInfo):
        if len(v) != 24:
            raise ValueError(f"{info.field_name} must have exactly 24 characters")
        if not re.fullmatch(r"[0-9a-fA-F]{24}", v):
            raise ValueError(
                f"{info.field_name} must contain only hexadecimal characters (0-9, a-f)"
            )
        return v.lower()
