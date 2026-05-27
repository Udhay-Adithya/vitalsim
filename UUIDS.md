# VitalsSim BLE UUID Reference

This simulator advertises as `VitalsSim` by default and exposes three GATT services with five read/notify characteristics.

## Dart Imports

Use these imports for the decoding snippets below:

```dart
import 'dart:typed_data';
```

## Services

| Service | UUID | Type | Purpose |
|---|---|---|---|
| Heart Rate | `0000180d-0000-1000-8000-00805f9b34fb` | Standard | Standard BLE Heart Rate service |
| Battery | `0000180f-0000-1000-8000-00805f9b34fb` | Standard | Standard BLE Battery service |
| Custom Vitals | `12345678-1234-1234-1234-123456789abc` | Custom | Non-standard vitals that do not have standard service coverage here |

## Characteristics

| Characteristic | Service UUID | Characteristic UUID | Properties | Byte Encoding | Dart Decode |
|---|---|---|---|---|---|
| Heart Rate Measurement | `0000180d-0000-1000-8000-00805f9b34fb` | `00002a37-0000-1000-8000-00805f9b34fb` | READ, NOTIFY | `[flags_uint8, bpm_uint8]`. This simulator sends `flags=0x00`, meaning the BPM value is an unsigned 8-bit integer in byte 1. | `final bpm = data[1];` |
| Battery Level | `0000180f-0000-1000-8000-00805f9b34fb` | `00002a19-0000-1000-8000-00805f9b34fb` | READ, NOTIFY | `[percent_uint8]`, range `0..100`. | `final batteryPercent = data[0];` |
| SpO2 | `12345678-1234-1234-1234-123456789abc` | `12345678-1234-1234-1234-123456789001` | READ, NOTIFY | `[percent_uint8]`, range `0..100`. | `final spo2Percent = data[0];` |
| Temperature | `12345678-1234-1234-1234-123456789abc` | `12345678-1234-1234-1234-123456789002` | READ, NOTIFY | `uint16` little-endian centidegrees Celsius. Example: `3670` means `36.70 C`. | `final tempC = ByteData.sublistView(Uint8List.fromList(data)).getUint16(0, Endian.little) / 100.0;` |
| Step Count | `12345678-1234-1234-1234-123456789abc` | `12345678-1234-1234-1234-123456789003` | READ, NOTIFY | `uint32` little-endian monotonically increasing step count. | `final steps = ByteData.sublistView(Uint8List.fromList(data)).getUint32(0, Endian.little);` |

## flutter_reactive_ble UUID Constants

```dart
final heartRateServiceUuid = Uuid.parse('0000180d-0000-1000-8000-00805f9b34fb');
final heartRateMeasurementUuid = Uuid.parse('00002a37-0000-1000-8000-00805f9b34fb');

final batteryServiceUuid = Uuid.parse('0000180f-0000-1000-8000-00805f9b34fb');
final batteryLevelUuid = Uuid.parse('00002a19-0000-1000-8000-00805f9b34fb');

final customVitalsServiceUuid = Uuid.parse('12345678-1234-1234-1234-123456789abc');
final spo2Uuid = Uuid.parse('12345678-1234-1234-1234-123456789001');
final temperatureUuid = Uuid.parse('12345678-1234-1234-1234-123456789002');
final stepsUuid = Uuid.parse('12345678-1234-1234-1234-123456789003');
```

## Exact Dart Decoders

### Heart Rate Measurement

```dart
int decodeHeartRate(List<int> data) {
  if (data.length < 2) {
    throw FormatException('Heart Rate Measurement requires at least 2 bytes');
  }

  final flags = data[0];
  final isUint16 = (flags & 0x01) == 0x01;

  if (isUint16) {
    if (data.length < 3) {
      throw FormatException('uint16 heart rate requires 3 bytes');
    }
    return ByteData.sublistView(Uint8List.fromList(data)).getUint16(1, Endian.little);
  }

  return data[1];
}
```

### Battery Level

```dart
int decodeBatteryLevel(List<int> data) {
  if (data.isEmpty) {
    throw FormatException('Battery Level requires 1 byte');
  }
  return data[0];
}
```

### SpO2

```dart
int decodeSpo2(List<int> data) {
  if (data.isEmpty) {
    throw FormatException('SpO2 requires 1 byte');
  }
  return data[0];
}
```

### Temperature

```dart
double decodeTemperatureC(List<int> data) {
  if (data.length < 2) {
    throw FormatException('Temperature requires 2 bytes');
  }
  final centidegrees = ByteData.sublistView(Uint8List.fromList(data))
      .getUint16(0, Endian.little);
  return centidegrees / 100.0;
}
```

### Step Count

```dart
int decodeSteps(List<int> data) {
  if (data.length < 4) {
    throw FormatException('Step Count requires 4 bytes');
  }
  return ByteData.sublistView(Uint8List.fromList(data))
      .getUint32(0, Endian.little);
}
```

## Subscription Example

```dart
final characteristic = QualifiedCharacteristic(
  serviceId: customVitalsServiceUuid,
  characteristicId: spo2Uuid,
  deviceId: deviceId,
);

final subscription = flutterReactiveBle
    .subscribeToCharacteristic(characteristic)
    .listen((data) {
  final spo2 = decodeSpo2(data);
  // Update app state with spo2.
});
```
