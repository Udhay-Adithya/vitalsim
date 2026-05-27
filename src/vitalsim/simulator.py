"""Bless-backed BLE peripheral simulator."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from contextlib import suppress

from bless import BlessGATTCharacteristic, BlessServer
from bless.backends.characteristic import (
    GATTAttributePermissions,
    GATTCharacteristicProperties,
)

from vitalsim.banner import build_startup_banner, log_uuid_reference
from vitalsim.bless_compat import maybe_await
from vitalsim.constants import (
    BATTERY_LEVEL_CHAR_UUID,
    BATTERY_SERVICE_UUID,
    CHARACTERISTIC_NAMES,
    CHARACTERISTIC_SERVICE,
    CUSTOM_VITALS_SERVICE_UUID,
    HEART_RATE_CHAR_UUID,
    HEART_RATE_SERVICE_UUID,
    SPO2_CHAR_UUID,
    STEPS_CHAR_UUID,
    TEMP_CHAR_UUID,
)
from vitalsim.state import VitalsState

LOGGER = logging.getLogger("vitalsim")


class VitalsSimulator:
    """BLE peripheral that streams simulated vitals through GATT notifications."""

    def __init__(self, name: str, base_interval_ms: int) -> None:
        if base_interval_ms <= 0:
            raise ValueError("--interval must be a positive integer")

        self.name = name
        self.base_interval_ms = base_interval_ms
        self.state = VitalsState()
        self.server = BlessServer(name=self.name)
        self.server.read_request_func = self._read_handler
        self.server.write_request_func = self._write_handler
        self._characteristics: dict[str, BlessGATTCharacteristic] = {}
        self._stop_event = asyncio.Event()
        self._update_task: asyncio.Task[None] | None = None
        self._server_started = False

    async def setup(self) -> None:
        """Create all GATT services and characteristics."""
        await maybe_await(self.server.add_new_service(HEART_RATE_SERVICE_UUID))
        await self._add_characteristic(
            HEART_RATE_SERVICE_UUID,
            HEART_RATE_CHAR_UUID,
            self.state.to_bytes(HEART_RATE_CHAR_UUID),
        )

        await maybe_await(self.server.add_new_service(BATTERY_SERVICE_UUID))
        await self._add_characteristic(
            BATTERY_SERVICE_UUID,
            BATTERY_LEVEL_CHAR_UUID,
            self.state.to_bytes(BATTERY_LEVEL_CHAR_UUID),
        )

        await maybe_await(self.server.add_new_service(CUSTOM_VITALS_SERVICE_UUID))
        await self._add_characteristic(
            CUSTOM_VITALS_SERVICE_UUID,
            SPO2_CHAR_UUID,
            self.state.to_bytes(SPO2_CHAR_UUID),
        )
        await self._add_characteristic(
            CUSTOM_VITALS_SERVICE_UUID,
            TEMP_CHAR_UUID,
            self.state.to_bytes(TEMP_CHAR_UUID),
        )
        await self._add_characteristic(
            CUSTOM_VITALS_SERVICE_UUID,
            STEPS_CHAR_UUID,
            self.state.to_bytes(STEPS_CHAR_UUID),
        )

    async def start(self) -> None:
        """Start BLE advertising and run until stopped."""
        try:
            await maybe_await(self.server.start())
        except (OSError, RuntimeError, PermissionError) as exc:
            LOGGER.error(
                "Failed to start BLE advertising: %s\n"
                "Likely causes: Bluetooth is disabled, permission was denied, "
                "BLE peripheral mode is unavailable, or another process is using "
                "the Bluetooth adapter.",
                exc,
            )
            raise

        self._server_started = True
        LOGGER.info(build_startup_banner(self.name))
        log_uuid_reference()

        self._update_task = asyncio.create_task(self._update_loop())
        try:
            await self._stop_event.wait()
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop update processing and BLE advertising cleanly."""
        self._stop_event.set()

        if self._update_task and not self._update_task.done():
            self._update_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._update_task

        if not self._server_started:
            return

        try:
            await maybe_await(self.server.stop())
        except (OSError, RuntimeError) as exc:
            LOGGER.warning("BLE server stop reported an error: %s", exc)
        else:
            LOGGER.info("BLE server stopped.")
        finally:
            self._server_started = False

    async def _add_characteristic(
        self,
        service_uuid: str,
        char_uuid: str,
        initial_value: bytearray,
    ) -> None:
        properties = (
            GATTCharacteristicProperties.read
            | GATTCharacteristicProperties.notify
        )
        permissions = GATTAttributePermissions.readable
        await maybe_await(
            self.server.add_new_characteristic(
                service_uuid,
                char_uuid,
                properties,
                None,
                permissions,
            )
        )

        characteristic = self._lookup_characteristic(char_uuid)
        if characteristic is None:
            raise RuntimeError(f"Could not register characteristic {char_uuid}")

        self._characteristics[char_uuid] = characteristic

    async def _update_loop(self) -> None:
        """Run per-characteristic update schedules using a configurable base tick."""
        tick = 0
        base_seconds = self.base_interval_ms / 1000.0

        intervals = {
            HEART_RATE_CHAR_UUID: self._seconds_to_ticks(1),
            BATTERY_LEVEL_CHAR_UUID: self._seconds_to_ticks(5),
            SPO2_CHAR_UUID: self._seconds_to_ticks(2),
            TEMP_CHAR_UUID: self._seconds_to_ticks(3),
            STEPS_CHAR_UUID: self._seconds_to_ticks(2),
        }

        while not self._stop_event.is_set():
            await asyncio.sleep(base_seconds)
            tick += 1

            for char_uuid, interval_ticks in intervals.items():
                if tick % interval_ticks == 0:
                    service_uuid = CHARACTERISTIC_SERVICE[char_uuid]
                    await self._update_characteristic(service_uuid, char_uuid)

            LOGGER.info(self.state.format_line(tick))

    async def _update_characteristic(self, service_uuid: str, char_uuid: str) -> None:
        """Update state, set the characteristic bytes, and notify subscribers."""
        updater: dict[str, Callable[[], int]] = {
            HEART_RATE_CHAR_UUID: self.state.update_heart_rate,
            BATTERY_LEVEL_CHAR_UUID: self.state.update_battery,
            SPO2_CHAR_UUID: self.state.update_spo2,
            TEMP_CHAR_UUID: self.state.update_temperature,
            STEPS_CHAR_UUID: self.state.update_steps,
        }

        updater[char_uuid]()
        characteristic = self._characteristics[char_uuid]
        characteristic.value = self.state.to_bytes(char_uuid)

        try:
            await maybe_await(self.server.update_value(service_uuid, char_uuid))
        except (OSError, RuntimeError, AttributeError) as exc:
            LOGGER.warning(
                "Could not notify %s (%s): %s",
                CHARACTERISTIC_NAMES[char_uuid],
                char_uuid,
                exc,
            )

    def _read_handler(
        self,
        characteristic: BlessGATTCharacteristic,
        **_: object,
    ) -> bytearray:
        """Return the current encoded value when a central reads a characteristic."""
        char_uuid = str(characteristic.uuid).lower()
        LOGGER.debug("Read request for %s", char_uuid)
        return self.state.to_bytes(char_uuid)

    def _write_handler(
        self,
        characteristic: BlessGATTCharacteristic,
        value: bytearray,
        **_: object,
    ) -> None:
        """Reject writes; all simulator characteristics are read/notify only."""
        LOGGER.debug(
            "Ignoring write request for read-only characteristic %s: %r",
            characteristic.uuid,
            bytes(value),
        )

    def _seconds_to_ticks(self, seconds: int) -> int:
        return max(1, round((seconds * 1000) / self.base_interval_ms))

    def _lookup_characteristic(
        self,
        char_uuid: str,
    ) -> BlessGATTCharacteristic | None:
        """Find a characteristic using the public bless lookup when available."""
        get_characteristic = getattr(self.server, "get_characteristic", None)
        if callable(get_characteristic):
            characteristic = get_characteristic(char_uuid)
            if characteristic is not None:
                return characteristic

        services = getattr(self.server, "services", None)
        if services is None:
            return None

        for service in getattr(services, "services", {}).values():
            for characteristic in getattr(service, "characteristics", []):
                if str(characteristic.uuid).lower() == char_uuid.lower():
                    return characteristic
        return None
