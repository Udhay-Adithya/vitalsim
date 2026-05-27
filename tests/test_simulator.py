"""Tests for Bless server integration behavior that can be verified without BLE."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from vitalsim.constants import HEART_RATE_CHAR_UUID
from vitalsim.simulator import VitalsSimulator


class FakeCharacteristic:
    def __init__(self, uuid: str) -> None:
        self.uuid = uuid
        self.value = bytearray()


class FakeBlessServer:
    def __init__(self, name: str) -> None:
        self.name = name
        self.read_request_func = None
        self.write_request_func = None
        self.characteristics: dict[str, FakeCharacteristic] = {}
        self.added_values: list[bytearray | None] = []

    def add_new_service(self, uuid: str) -> None:
        self.service_uuid = uuid

    def add_new_characteristic(
        self,
        service_uuid: str,
        char_uuid: str,
        properties: object,
        value: bytearray | None,
        permissions: object,
    ) -> None:
        self.characteristics[char_uuid] = FakeCharacteristic(char_uuid)
        self.added_values.append(value)

    def get_characteristic(self, char_uuid: str) -> FakeCharacteristic | None:
        return self.characteristics.get(char_uuid)


class VitalsSimulatorSetupTests(unittest.IsolatedAsyncioTestCase):
    async def test_characteristics_are_registered_without_cached_values(self) -> None:
        with patch("vitalsim.simulator.BlessServer", FakeBlessServer):
            simulator = VitalsSimulator(name="VitalsSim", base_interval_ms=1000)
            await simulator.setup()

        self.assertEqual(len(simulator.server.added_values), 5)
        self.assertEqual(simulator.server.added_values, [None, None, None, None, None])
        self.assertEqual(
            simulator._read_handler(FakeCharacteristic(HEART_RATE_CHAR_UUID)),
            bytearray([0x00, 78]),
        )


if __name__ == "__main__":
    unittest.main()
