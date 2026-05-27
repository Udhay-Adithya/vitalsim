# VitalsSim

VitalsSim is a Python Bluetooth Low Energy peripheral simulator for testing BLE central clients that scan, connect, discover GATT services, and subscribe to live vitals notifications.

It is built on [`bless`](https://github.com/kevincar/bless) and acts as the BLE server/peripheral. Any BLE central can consume it, including native mobile apps, desktop tools, web clients with Web Bluetooth support, and test harnesses.

## Features

- Advertises as `VitalsSim` by default
- Standard BLE Heart Rate service
- Standard BLE Battery service
- Custom Vitals service for SpO2, temperature, and step count
- Read and notify support for all five characteristics
- Per-characteristic update schedules
- Reproducible random simulation with `--seed`
- Asyncio-only runtime, no threads

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- Bluetooth hardware that supports BLE peripheral mode
- Platform support through `bless`

Linux also needs:

```bash
sudo apt install bluetooth bluez libglib2.0-dev
```

On Linux, BLE peripheral mode typically requires `sudo` or suitable Bluetooth permissions. On macOS, run without `sudo` and grant Bluetooth permission on first run if prompted. Windows peripheral support is limited.

## Install

Clone the repository, then install dependencies with uv:

```bash
uv sync
```

For development tools:

```bash
uv sync --dev
```

## Run

Recommended on macOS and most developer machines:

```bash
uv run vitalsim
```

On Linux, use `sudo` if your Bluetooth permissions require it:

```bash
sudo uv run vitalsim
```

Useful options:

```bash
uv run vitalsim --name VitalsSim
uv run vitalsim --interval 1000
uv run vitalsim --seed 1234
uv run vitalsim --verbose
```

`--interval` is the base scheduler tick in milliseconds. The default is `1000`, which means:

- Heart rate updates every 1 second
- SpO2 updates every 2 seconds
- Steps update every 2 seconds
- Temperature updates every 3 seconds
- Battery updates every 5 seconds

## BLE GATT Layout

| Service | Characteristic | UUID | Encoding |
|---|---|---|---|
| Heart Rate `0000180d-0000-1000-8000-00805f9b34fb` | Heart Rate Measurement | `00002a37-0000-1000-8000-00805f9b34fb` | `[flags_uint8, bpm_uint8]` |
| Battery `0000180f-0000-1000-8000-00805f9b34fb` | Battery Level | `00002a19-0000-1000-8000-00805f9b34fb` | `[percent_uint8]` |
| Custom Vitals `12345678-1234-1234-1234-123456789abc` | SpO2 | `12345678-1234-1234-1234-123456789001` | `[percent_uint8]` |
| Custom Vitals `12345678-1234-1234-1234-123456789abc` | Temperature | `12345678-1234-1234-1234-123456789002` | `uint16` little-endian centidegrees Celsius |
| Custom Vitals `12345678-1234-1234-1234-123456789abc` | Step Count | `12345678-1234-1234-1234-123456789003` | `uint32` little-endian steps |

See [UUIDS.md](UUIDS.md) for the full UUID and byte-format reference.

## Client Decode Examples

These examples focus on decoding notification payloads after your client has connected and subscribed to the relevant characteristic.

### JavaScript

Useful for Web Bluetooth clients and Node-based BLE clients that expose payloads as `DataView`, `ArrayBuffer`, or `Buffer`.

```js
function asDataView(value) {
  if (value instanceof DataView) return value;
  if (value instanceof ArrayBuffer) return new DataView(value);
  return new DataView(value.buffer, value.byteOffset, value.byteLength);
}

function decodeHeartRate(value) {
  const data = asDataView(value);
  const flags = data.getUint8(0);
  return (flags & 0x01) === 0x01 ? data.getUint16(1, true) : data.getUint8(1);
}

function decodeBattery(value) {
  return asDataView(value).getUint8(0);
}

function decodeSpo2(value) {
  return asDataView(value).getUint8(0);
}

function decodeTemperatureC(value) {
  return asDataView(value).getUint16(0, true) / 100;
}

function decodeSteps(value) {
  return asDataView(value).getUint32(0, true);
}
```

### Swift

Useful for iOS, iPadOS, macOS, watchOS, and other CoreBluetooth clients.

```swift
import Foundation

func decodeHeartRate(_ data: Data) -> UInt16 {
    let flags = data[0]
    if flags & 0x01 == 0x01 {
        return UInt16(data[1]) | (UInt16(data[2]) << 8)
    }
    return UInt16(data[1])
}

func decodeBattery(_ data: Data) -> UInt8 {
    data[0]
}

func decodeSpo2(_ data: Data) -> UInt8 {
    data[0]
}

func decodeTemperatureC(_ data: Data) -> Double {
    let centidegrees = UInt16(data[0]) | (UInt16(data[1]) << 8)
    return Double(centidegrees) / 100.0
}

func decodeSteps(_ data: Data) -> UInt32 {
    UInt32(data[0])
        | (UInt32(data[1]) << 8)
        | (UInt32(data[2]) << 16)
        | (UInt32(data[3]) << 24)
}
```

### Kotlin

Useful for Android BLE clients.

```kotlin
import java.nio.ByteBuffer
import java.nio.ByteOrder

fun decodeHeartRate(bytes: ByteArray): Int {
    val flags = bytes[0].toInt()
    return if ((flags and 0x01) == 0x01) {
        ByteBuffer.wrap(bytes, 1, 2).order(ByteOrder.LITTLE_ENDIAN).short.toInt() and 0xffff
    } else {
        bytes[1].toInt() and 0xff
    }
}

fun decodeBattery(bytes: ByteArray): Int = bytes[0].toInt() and 0xff

fun decodeSpo2(bytes: ByteArray): Int = bytes[0].toInt() and 0xff

fun decodeTemperatureC(bytes: ByteArray): Double {
    val centidegrees = ByteBuffer.wrap(bytes, 0, 2)
        .order(ByteOrder.LITTLE_ENDIAN)
        .short
        .toInt() and 0xffff
    return centidegrees / 100.0
}

fun decodeSteps(bytes: ByteArray): Long {
    return ByteBuffer.wrap(bytes, 0, 4)
        .order(ByteOrder.LITTLE_ENDIAN)
        .int
        .toLong() and 0xffffffffL
}
```

## Development

Run tests:

```bash
uv run python -m unittest discover -s tests
```

Lint:

```bash
uv run ruff check .
```

Build a wheel:

```bash
uv build
```

## Project Layout

```text
.
├── pyproject.toml            # uv/project metadata and dependencies
├── README.md
├── UUIDS.md
├── LICENSE
├── src/vitalsim/
│   ├── cli.py                # argparse and process entry point
│   ├── simulator.py          # bless server and notify loop
│   ├── state.py              # random-walk vitals and byte encoding
│   ├── constants.py          # GATT UUIDs
│   └── platform_notes.py
└── tests/
    ├── test_simulator.py
    └── test_state.py
```

## License

MIT. See [LICENSE](LICENSE).
