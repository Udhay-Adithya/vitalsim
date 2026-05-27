# VitalsSim

VitalsSim is a Python Bluetooth Low Energy peripheral simulator for testing mobile apps that scan, connect, discover GATT services, and subscribe to live vitals notifications.

It is built on [`bless`](https://github.com/kevincar/bless) and acts as the BLE server/peripheral. Your Flutter app, for example one using `flutter_reactive_ble`, acts as the BLE client/central.

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

Recommended:

```bash
uv run vitalsim
```

Compatibility wrapper:

```bash
uv run python ble_simulator.py
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

See [UUIDS.md](UUIDS.md) for exact Dart decoding snippets for `flutter_reactive_ble`.

## Flutter Subscription Sketch

```dart
final characteristic = QualifiedCharacteristic(
  serviceId: Uuid.parse('12345678-1234-1234-1234-123456789abc'),
  characteristicId: Uuid.parse('12345678-1234-1234-1234-123456789001'),
  deviceId: deviceId,
);

final subscription = flutterReactiveBle
    .subscribeToCharacteristic(characteristic)
    .listen((data) {
  final spo2 = data[0];
  // Update app state.
});
```

## Development

Run tests:

```bash
PYTHONPATH=src uv run python -m unittest
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
├── ble_simulator.py          # Compatibility wrapper
├── pyproject.toml            # uv/project metadata and dependencies
├── README.md
├── UUIDS.md
├── src/vitalsim/
│   ├── cli.py                # argparse and process entry point
│   ├── simulator.py          # bless server and notify loop
│   ├── state.py              # random-walk vitals and byte encoding
│   ├── constants.py          # GATT UUIDs
│   └── platform_notes.py
└── tests/
    └── test_state.py
```

## License

MIT
