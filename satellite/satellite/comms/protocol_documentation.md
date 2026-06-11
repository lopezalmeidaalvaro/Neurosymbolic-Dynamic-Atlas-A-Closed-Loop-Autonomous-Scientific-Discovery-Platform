# Space Communications Protocol Stack (T68)

This document contains structural descriptions, binary layouts, and CRC-8 calculation details for the communications layers implemented in `space_protocol_stack.py`.

---

## 1. CCSDS Space Packet Protocol (CCSDS 133.0-B-1)

Used for primary spacecraft-to-ground telemetry and command transfers.

### Binary Header Structure (6 Bytes Primary Header)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|V.N|T|S|       APID            |Seq.F|      Sequence Count     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Packet Data Length      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Fields Definition
* **Version Number (V.N)**: 3 bits (always set to `000` for class-1 version).
* **Type (T)**: 1 bit (0 for telemetry, 1 for commands).
* **Secondary Header Flag (S)**: 1 bit (0 if absent, 1 if present).
* **APID** (Application Process Identifier): 11 bits. Represents individual thermal node streams (APID 16-21).
* **Sequence Flags (Seq.F)**: 2 bits (3 indicates unsegmented data).
* **Sequence Count**: 14 bits (increases sequentially by 1).
* **Packet Data Length**: 16 bits (actual size of payload in bytes minus 1).

---

## 2. SpaceWire Routing Protocol (ECSS-E-ST-50-12C)

Low-latency inter-instrument routing format used inside the spacecraft backplane.

### Packet Format

```
+-----------------+-----------------+-----------------+-----------------+
| Logical Address |   Protocol ID   |     Payload     |      CRC-8      |
|    (1 Byte)     |    (1 Byte)     |    (N Bytes)    |    (1 Byte)     |
+-----------------+-----------------+-----------------+-----------------+
```

* **Logical Address**: Destination router path address (e.g. `0xFE`).
* **Protocol ID**: Identifies the transport protocol layer (e.g. `0x06` for thermal service).
* **CRC-8 Checksum**: Protection calculated using the polynomial:
  
  $$x^8 + x^2 + x^1 + 1 \quad (\text{poly } 0\text{x}07)$$

---

## 3. CAN Aerospace 2.0B

Robust CAN bus standard used inside satellite nodes.

### Frame Layout
* **CAN Identifier**: 29-bit extended identifier.
  * Thermal telemetry range is mapped to `0x700` (Node 0) up to `0x70F` (Node 15).
* **Payload**: 8 bytes.
  * Float 32-bit Temperature (4 bytes, Little-Endian)
  * Float 32-bit Power (4 bytes, Little-Endian)

---

## 4. CubeSat Space Protocol (CSP)

Extremely popular ad-hoc networking protocol for cubesats.

### Thermal Command Services (Port 15)
* **Header**: 2-byte routing header containing Source Port (5 bits), Destination Port (5 bits), and active command code (6 bits).
* **Commands**:
  * `0x01`: `CSP_THERMAL_PREDICT` -> Queries look-ahead EKF forecasts.
  * `0x02`: `CSP_THERMAL_STATUS` -> Returns sensor status codes.
  * `0x03`: `CSP_THROTTLE` -> Sets CPU active thermal throttling caps.
* **Payload**: 32-bit float value.
