"""Pure-Python vitals state simulation and GATT byte encoding."""

from __future__ import annotations

import random
import struct
from dataclasses import dataclass

from vitalsim.constants import (
    BATTERY_LEVEL_CHAR_UUID,
    HEART_RATE_CHAR_UUID,
    SPO2_CHAR_UUID,
    STEPS_CHAR_UUID,
    TEMP_CHAR_UUID,
)


def clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer into an inclusive range."""
    return max(minimum, min(maximum, value))


@dataclass
class VitalsState:
    """Current simulated vital values and byte encoders."""

    heart_rate: int = 78
    battery: int = 100
    spo2: int = 98
    temperature_centidegrees: int = 3670
    steps: int = 0

    def update_heart_rate(self) -> int:
        self.heart_rate = clamp(self.heart_rate + random.randint(-3, 3), 55, 105)
        return self.heart_rate

    def update_battery(self) -> int:
        self.battery = clamp(self.battery - random.randint(0, 1), 0, 100)
        return self.battery

    def update_spo2(self) -> int:
        self.spo2 = clamp(self.spo2 + random.randint(-1, 1), 93, 100)
        return self.spo2

    def update_temperature(self) -> int:
        self.temperature_centidegrees = clamp(
            self.temperature_centidegrees + random.randint(-5, 5),
            3600,
            3800,
        )
        return self.temperature_centidegrees

    def update_steps(self) -> int:
        self.steps += random.randint(0, 5)
        return self.steps

    def to_bytes(self, char_uuid: str) -> bytearray:
        """Encode the current value for a characteristic UUID."""
        normalized_uuid = char_uuid.lower()
        if normalized_uuid == HEART_RATE_CHAR_UUID:
            return bytearray([0x00, self.heart_rate])
        if normalized_uuid == BATTERY_LEVEL_CHAR_UUID:
            return bytearray([self.battery])
        if normalized_uuid == SPO2_CHAR_UUID:
            return bytearray([self.spo2])
        if normalized_uuid == TEMP_CHAR_UUID:
            return bytearray(struct.pack("<H", self.temperature_centidegrees))
        if normalized_uuid == STEPS_CHAR_UUID:
            return bytearray(struct.pack("<I", self.steps))
        raise ValueError(f"Unknown characteristic UUID: {char_uuid}")

    def format_line(self, tick: int) -> str:
        """Format the current vitals for one-line console logging."""
        temperature_c = self.temperature_centidegrees / 100.0
        return (
            f"[tick={tick}] HR={self.heart_rate}bpm  "
            f"SpO2={self.spo2}%  "
            f"Temp={temperature_c:.1f}°C  "
            f"Steps={self.steps}  "
            f"Bat={self.battery}%"
        )
