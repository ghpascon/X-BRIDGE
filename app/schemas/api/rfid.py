import re
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class TagRequest(BaseModel):
    device: Optional[str] = Field("DEVICE_01")
    epc: str = Field("000000000000000000000001")
    tid: Optional[str] = Field("000000000000000000000002")
    ant: int = 1
    rssi: int = -80

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
    STORAGE_DAYS: int = 7
    LOG_PATH: str = Field("Logs")


class InventoryRequest(BaseModel):
    device: str = Field("DEVICE_01")
    state: bool = True


rfid_base_responses = {
    200: {
        "description": "Success",
        "content": {"application/json": {"example": {"msg": "success"}}},
    },
    422: {
        "description": "Error",
        "content": {"application/json": {"example": {"detail": "error"}}},
    },
}

rfid_actions_responses = {
    200: {
        "description": "Success",
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
        "description": "Error",
        "content": {"application/json": {"example": {"detail": "error"}}},
    },
}
