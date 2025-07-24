import re
from typing import Optional, Any

from pydantic import BaseModel, Field, ValidationInfo, field_validator

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
            raise ValueError(f"{info.field_name} must contain only hexadecimal characters (0-9, a-f)")
        return v

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


class RfidRequest(BaseModel):
    HTTP_POST: Optional[str] = Field("http://localhost:5001")
    DATABASE_URL: Optional[str] = Field(
        "mysql+aiomysql://root:admin@localhost:3306/middleware_smartx"
    )
    STORAGE_DAYS: int = Field(7)
    LOG_PATH: str = Field("Logs")


class InventoryRequest(BaseModel):
    device: str = Field("DEVICE01")
    state: bool = True


class EventRequest(BaseModel):
    device: str = Field("DEVICE01")
    event_type: str = Field("event_type")
    event_data: Any = {"data": "xyz"}


class SetGpoRequest(BaseModel):
    gpo_pin: Optional[int] = Field(1)
    state: Optional[bool] = Field(True)
    control: Optional[str] = Field("static")
    time: Optional[int] = Field(1000)


# === Swagger Response Models ===

gpo_responses = {
    200: {
        "description": "GPO command executed successfully",
        "content": {"application/json": {"example": {"msg": "GPO DEVICE_01, True"}}},
    },
    400: {
        "description": "Invalid device",
        "content": {"application/json": {"example": {"detail": "Invalid device"}}},
    },
    404: {
        "description": "No GPO found for device",
        "content": {"application/json": {"example": {"msg": "No Gpo"}}},
    },
    422: {
        "description": "Validation error",
        "content": {"application/json": {"example": {"detail": "Invalid device"}}},
    },
    500: {
        "description": "Internal Server Error",
        "content": {"application/json": {"example": {"msg": "Exception message"}}},
    },
}

rfid_base_responses = {
    200: {
        "description": "Operation successful",
        "content": {"application/json": {"example": {"msg": "success"}}},
    },
    422: {
        "description": "Validation error",
        "content": {"application/json": {"example": {"detail": "error"}}},
    },
}

rfid_actions_responses = {
    200: {
        "description": "RFID action settings returned successfully",
        "content": {
            "application/json": {
                "example": {
                    "HTTP_POST": "http://localhost:5001",
                    "DATABASE_URL": "mysql+aiomysql://root:admin@localhost:3306/middleware_smartx",
                    "STORAGE_DAYS": 7,
                    "LOG_PATH": "Logs",
                }
            }
        },
    },
    422: {
        "description": "Invalid input or action",
        "content": {"application/json": {"example": {"detail": "error"}}},
    },
}
