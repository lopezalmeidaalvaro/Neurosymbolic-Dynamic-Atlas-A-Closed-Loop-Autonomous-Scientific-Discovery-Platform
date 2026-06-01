# Real-Time WebSocket Streaming Architecture

This module implements low-latency mission control streams, Redis Pub/Sub broadcasters, and accelerated historical simulation replays.

---

## 1. WebSocket Server Routes

Exposes three async communication channels:
1. `WS /ws/telemetry/{mission_id}`: Relays live sensor telemetry updates.
2. `WS /ws/ekf/{mission_id}`: Relays EKF parameter and state estimation updates.
3. `WS /ws/fleet`: Relays 10s aggregated fleet metrics.
4. `WS /ws/replay/{mission_id}?speed=60x`: Relays accelerated historical records.

---

## 2. Dynamic Replay Speeds

The historical database playback speed is configured via the `speed` query parameter:
* **1x**: standard real-time orbit replay (120s step delays).
* **10x**: fast replay (12s step delays).
* **60x**: 1-minute orbit replay (2s step delays).
* **600x**: instant presentation playback (0.2s step delays).

---

## 3. Message Payload Format

```json
{
  "type": "telemetry",
  "mission_id": "c4b8e212-0000-4000-a000-000000000001",
  "timestamp": "2026-05-29T10:30:00Z",
  "data": {
    "temperatures": {
      "CPU": 45.2,
      "Battery": 22.1,
      "Payload": 20.3,
      "Structure": 22.0,
      "Radiator": 30.1,
      "SolarPanels": 35.4
    },
    "power": 15.0,
    "emissivity": 0.85,
    "anomaly_flags": []
  }
}
```
