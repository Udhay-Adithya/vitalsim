"""VitalsSim BLE peripheral simulator package."""

from vitalsim.constants import (
    BATTERY_LEVEL_CHAR_UUID,
    BATTERY_SERVICE_UUID,
    CUSTOM_VITALS_SERVICE_UUID,
    DEVICE_NAME_DEFAULT,
    HEART_RATE_CHAR_UUID,
    HEART_RATE_SERVICE_UUID,
    SPO2_CHAR_UUID,
    STEPS_CHAR_UUID,
    TEMP_CHAR_UUID,
)
from vitalsim.state import VitalsState

__all__ = [
    "BATTERY_LEVEL_CHAR_UUID",
    "BATTERY_SERVICE_UUID",
    "CUSTOM_VITALS_SERVICE_UUID",
    "DEVICE_NAME_DEFAULT",
    "HEART_RATE_CHAR_UUID",
    "HEART_RATE_SERVICE_UUID",
    "SPO2_CHAR_UUID",
    "STEPS_CHAR_UUID",
    "TEMP_CHAR_UUID",
    "VitalsState",
]
