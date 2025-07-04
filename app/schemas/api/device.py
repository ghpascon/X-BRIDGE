from pydantic import BaseModel
from typing import Tuple

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


# === Swagger Response Examples ===

device_list_responses = {
    200: {
        "description": "List of all registered device names.",
        "content": {
            "application/json": {
                "example": ["device_01", "device_02"]
            }
        },
    }
}

device_responses = {
    200: {
        "description": "Successful operation.",
        "content": {
            "application/json": {
                "example": {"msg": "success"}
            }
        },
    },
    422: {
        "description": "Device validation error.",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_device": {
                        "summary": "Invalid device name",
                        "value": {"detail": "Invalid Device"}
                    },
                    "device_not_connected": {
                        "summary": "Device is disconnected",
                        "value": {"detail": "Device is not connected"}
                    },
                }
            }
        },
    },
    500: {
        "description": "Unexpected internal error.",
        "content": {
            "application/json": {
                "example": {"detail": "Internal Server Error"}
            }
        },
    },
}

config_responses = {
    200: {
        "description": "Returns the configuration of the specified device.",
        "content": {
            "application/json": {
                "example": {
                    "READER": "X714",
                    "CONNECTION": "COM5",
                    "PARAMETER": "VALUE"
                }
            }
        },
    },
    422: {
        "description": "Invalid device or configuration error.",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid Device"}
            }
        },
    },
    500: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "example": {"detail": "Internal Server Error"}
            }
        },
    },
}

state_responses = {
    200: {
        "description": "Returns the current reading state of the device.",
        "content": {
            "application/json": {
                "examples": {
                    "idle": {
                        "summary": "Device is idle",
                        "value": {"state": "idle"}
                    },
                    "running": {
                        "summary": "Device is actively reading",
                        "value": {"state": "running"}
                    },
                }
            }
        },
    },
    422: {
        "description": "Device validation error.",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_device": {
                        "summary": "Invalid device name",
                        "value": {"detail": "Invalid Device"}
                    },
                    "device_not_connected": {
                        "summary": "Device is disconnected",
                        "value": {"detail": "Device is not connected"}
                    },
                }
            }
        },
    },
    500: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "example": {"detail": "Internal Server Error"}
            }
        },
    },
}
