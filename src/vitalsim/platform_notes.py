"""Platform-specific startup diagnostics."""

from __future__ import annotations

import logging
import os
import sys

LOGGER = logging.getLogger("vitalsim")


def log_platform_notes() -> None:
    """Log useful platform guidance before starting the BLE server."""
    if sys.platform.startswith("linux"):
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            LOGGER.warning("Warning: on Linux, BLE peripheral mode typically requires sudo")
        LOGGER.info("Linux backend: BlueZ D-Bus. Install bluetooth, bluez, libglib2.0-dev.")
    elif sys.platform == "darwin":
        LOGGER.info("macOS backend: CoreBluetooth. Grant Bluetooth permission if prompted.")
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            LOGGER.warning(
                "macOS usually should be run without sudo so Bluetooth permission prompts work."
            )
    elif sys.platform == "win32":
        LOGGER.warning("Windows BLE peripheral support is limited; results may vary.")
    else:
        LOGGER.info(
            "Platform %s detected; BLE peripheral support depends on bless backend.",
            sys.platform,
        )
