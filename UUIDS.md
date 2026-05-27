# VitalsSim BLE UUID Reference

This simulator advertises as `VitalsSim` by default and exposes three GATT services with five read/notify characteristics. All characteristic values are byte arrays.

## Services

| Service | UUID | Type | Purpose |
|---|---|---|---|
| Heart Rate | `0000180d-0000-1000-8000-00805f9b34fb` | Standard | Standard BLE Heart Rate service |
| Battery | `0000180f-0000-1000-8000-00805f9b34fb` | Standard | Standard BLE Battery service |
| Custom Vitals | `12345678-1234-1234-1234-123456789abc` | Custom | Non-standard vitals grouped under one service |

## Characteristics

| Characteristic | Service UUID | Characteristic UUID | Properties | Byte Encoding | Decode Rule |
|---|---|---|---|---|---|
| Heart Rate Measurement | `0000180d-0000-1000-8000-00805f9b34fb` | `00002a37-0000-1000-8000-00805f9b34fb` | READ, NOTIFY | `[flags_uint8, bpm]` | If bit 0 of `flags` is `0`, BPM is `uint8` at byte 1. If bit 0 is `1`, BPM is `uint16` little-endian at bytes 1-2. VitalsSim sends `flags=0x00`. |
| Battery Level | `0000180f-0000-1000-8000-00805f9b34fb` | `00002a19-0000-1000-8000-00805f9b34fb` | READ, NOTIFY | `[percent_uint8]` | Unsigned integer from byte 0, range `0..100`. |
| SpO2 | `12345678-1234-1234-1234-123456789abc` | `12345678-1234-1234-1234-123456789001` | READ, NOTIFY | `[percent_uint8]` | Unsigned integer from byte 0, range `0..100`. |
| Temperature | `12345678-1234-1234-1234-123456789abc` | `12345678-1234-1234-1234-123456789002` | READ, NOTIFY | `uint16` little-endian centidegrees Celsius | Decode bytes 0-1 as an unsigned little-endian integer, then divide by `100.0`. Example: `3670` means `36.70 C`. |
| Step Count | `12345678-1234-1234-1234-123456789abc` | `12345678-1234-1234-1234-123456789003` | READ, NOTIFY | `uint32` little-endian steps | Decode bytes 0-3 as an unsigned little-endian integer. |

## Update Schedule

| Characteristic | Interval | Simulation Behavior |
|---|---:|---|
| Heart Rate Measurement | 1 second | Random walk by `-3..3`, clamped to `55..105` bpm |
| Battery Level | 5 seconds | Decreases by `0..1`, clamped to `0..100` percent |
| SpO2 | 2 seconds | Random walk by `-1..1`, clamped to `93..100` percent |
| Temperature | 3 seconds | Random walk by `-5..5` centidegrees, clamped to `3600..3800` |
| Step Count | 2 seconds | Monotonically increases by `0..5` steps |

## UUID Constants

```text
HEART_RATE_SERVICE_UUID      = 0000180d-0000-1000-8000-00805f9b34fb
HEART_RATE_CHAR_UUID         = 00002a37-0000-1000-8000-00805f9b34fb

BATTERY_SERVICE_UUID         = 0000180f-0000-1000-8000-00805f9b34fb
BATTERY_LEVEL_CHAR_UUID      = 00002a19-0000-1000-8000-00805f9b34fb

CUSTOM_VITALS_SERVICE_UUID   = 12345678-1234-1234-1234-123456789abc
SPO2_CHAR_UUID               = 12345678-1234-1234-1234-123456789001
TEMP_CHAR_UUID               = 12345678-1234-1234-1234-123456789002
STEPS_CHAR_UUID              = 12345678-1234-1234-1234-123456789003
```
