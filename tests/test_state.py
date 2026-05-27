"""Tests for pure-Python vitals state encoding."""

from __future__ import annotations

import struct
import unittest

from vitalsim.constants import (
    BATTERY_LEVEL_CHAR_UUID,
    HEART_RATE_CHAR_UUID,
    SPO2_CHAR_UUID,
    STEPS_CHAR_UUID,
    TEMP_CHAR_UUID,
)
from vitalsim.state import VitalsState


class VitalsStateEncodingTests(unittest.TestCase):
    def test_encodes_all_characteristics(self) -> None:
        state = VitalsState(
            heart_rate=72,
            battery=99,
            spo2=97,
            temperature_centidegrees=3670,
            steps=12345,
        )

        self.assertEqual(state.to_bytes(HEART_RATE_CHAR_UUID), bytearray([0x00, 72]))
        self.assertEqual(state.to_bytes(BATTERY_LEVEL_CHAR_UUID), bytearray([99]))
        self.assertEqual(state.to_bytes(SPO2_CHAR_UUID), bytearray([97]))
        self.assertEqual(state.to_bytes(TEMP_CHAR_UUID), bytearray(struct.pack("<H", 3670)))
        self.assertEqual(state.to_bytes(STEPS_CHAR_UUID), bytearray(struct.pack("<I", 12345)))

    def test_update_ranges_are_clamped(self) -> None:
        state = VitalsState(
            heart_rate=500,
            battery=-1,
            spo2=500,
            temperature_centidegrees=9999,
        )

        self.assertLessEqual(state.update_heart_rate(), 105)
        self.assertGreaterEqual(state.update_battery(), 0)
        self.assertLessEqual(state.update_spo2(), 100)
        self.assertLessEqual(state.update_temperature(), 3800)


if __name__ == "__main__":
    unittest.main()
