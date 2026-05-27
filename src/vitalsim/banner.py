"""Console output helpers for VitalsSim."""

from __future__ import annotations

import logging

from vitalsim.constants import (
    BATTERY_LEVEL_CHAR_UUID,
    BATTERY_SERVICE_UUID,
    CUSTOM_VITALS_SERVICE_UUID,
    HEART_RATE_CHAR_UUID,
    HEART_RATE_SERVICE_UUID,
    SPO2_CHAR_UUID,
    STEPS_CHAR_UUID,
    TEMP_CHAR_UUID,
)

LOGGER = logging.getLogger("vitalsim")


def build_startup_banner(device_name: str) -> str:
    """Return the startup banner shown after BLE advertising starts."""
    return f"""
╔══════════════════════════════════════════╗
║         VitalsSim BLE Peripheral         ║
╠══════════════════════════════════════════╣
║  Device name : {device_name:<25.25}║
║  Services    : 3 (Heart Rate, Battery,   ║
║                   Custom Vitals)         ║
║  Advertising : YES                       ║
║  Press Ctrl+C to stop                    ║
╚══════════════════════════════════════════╝
""".rstrip()


def log_uuid_reference() -> None:
    """Log all advertised services and characteristics."""
    LOGGER.info(
        "Services: Heart Rate=%s, Battery=%s, Custom Vitals=%s",
        HEART_RATE_SERVICE_UUID,
        BATTERY_SERVICE_UUID,
        CUSTOM_VITALS_SERVICE_UUID,
    )
    LOGGER.info(
        "Characteristics: HR=%s, Battery=%s, SpO2=%s, Temperature=%s, Steps=%s",
        HEART_RATE_CHAR_UUID,
        BATTERY_LEVEL_CHAR_UUID,
        SPO2_CHAR_UUID,
        TEMP_CHAR_UUID,
        STEPS_CHAR_UUID,
    )
