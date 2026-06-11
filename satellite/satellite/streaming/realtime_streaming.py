#!/usr/bin/env python3
"""
Real-Time Streaming Architecture (T54)
Autonomous Spacecraft Thermal OS
Manages WebSocket streaming connections, Redis Pub/Sub broadcasts,
and accelerated historical simulation replays.
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from fastapi import WebSocket, WebSocketDisconnect

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from db.telemetry_warehouse import TelemetryWarehouse

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    import redis.asyncio as aioredis

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


class TelemetryStreamer:
    def __init__(self):
        self.redis = None
        self.active_connections = []
        if HAS_REDIS:
            try:
                self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
            except Exception as e:
                print(f"[Streaming] Redis async connection failed: {e}")

    async def connect_client(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect_client(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_local(self, message: dict):
        """Broadcasts directly to all connected WebSockets (in-memory fallback)."""
        payload = json.dumps(message)
        for conn in list(self.active_connections):
            try:
                await conn.send_text(payload)
            except Exception:
                self.disconnect_client(conn)

    async def publish_redis(self, channel: str, message: dict):
        """Publishes a JSON packet over a Redis Pub/Sub channel."""
        if HAS_REDIS and self.redis:
            try:
                await self.redis.publish(channel, json.dumps(message))
                return
            except Exception:
                pass
        # Fallback to local broadcast if Redis fails
        await self.broadcast_local(message)

    async def listen_and_stream(self, websocket: WebSocket, channel: str):
        """Listens to a Redis channel and relays messages to a specific client WebSocket."""
        await self.connect_client(websocket)

        if HAS_REDIS and self.redis:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            try:
                while True:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=1.0
                    )
                    if message:
                        await websocket.send_text(message["data"])
                    await asyncio.sleep(0.01)
            except WebSocketDisconnect:
                self.disconnect_client(websocket)
            finally:
                await pubsub.unsubscribe(channel)
        else:
            # Fallback keep-alive loop for local broadcasts
            try:
                while True:
                    await asyncio.sleep(1.0)
            except WebSocketDisconnect:
                self.disconnect_client(websocket)

    async def stream_historical_replay(
        self, websocket: WebSocket, mission_id: str, speed_factor: float = 1.0
    ):
        """Reads historical telemetry from TimescaleDB and replays it over WebSocket at accelerated speeds."""
        await websocket.accept()
        db = TelemetryWarehouse()

        # Fetch last 24 hours of telemetry data
        t_start = datetime.fromtimestamp(time.time() - 24 * 3600).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        t_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            records = db.query_telemetry_range(mission_id, t_start, t_end)
            if not records:
                # Fallback golden data for demonstration
                from demo.run_demo import generate_golden_telemetry

                telemetry = generate_golden_telemetry()
                records = [
                    {
                        "time": datetime.fromtimestamp(
                            time.time() + p["time"] * 60
                        ).isoformat(),
                        "node_id": "CPU",
                        "temperature": p["cpuTemp"],
                        "power": p["cpuPower"] if "cpuPower" in p else 15.0,
                        "radiator_state": (
                            p["emissivity"] if "emissivity" in p else 0.85
                        ),
                        "anomaly_flags": [],
                    }
                    for p in telemetry
                ]

            print(
                f"[Streaming] Starting replay for mission {mission_id} ({len(records)} points, Speed: {speed_factor}x)"
            )

            # Batch records by timestamp to simulate real steps
            grouped_records = {}
            for r in records:
                t = r["time"]
                if t not in grouped_records:
                    grouped_records[t] = []
                grouped_records[t].append(r)

            sorted_timestamps = sorted(grouped_records.keys())

            # Base step interval (scaled by speed factor)
            # Typically steps are recorded every 120s; at 60x speed, sleep = 120/60 = 2 seconds
            base_dt = 120.0
            sleep_interval = max(0.05, base_dt / speed_factor)

            for timestamp in sorted_timestamps:
                step_data = grouped_records[timestamp]
                payload = {
                    "type": "replay_telemetry",
                    "mission_id": mission_id,
                    "timestamp": str(timestamp),
                    "data": {
                        "temperatures": {
                            r["node_id"]: r["temperature"] for r in step_data
                        },
                        "power": step_data[0]["power"],
                        "emissivity": step_data[0]["radiator_state"],
                        "anomaly_flags": step_data[0]["anomaly_flags"],
                    },
                }
                await websocket.send_text(json.dumps(payload))
                await asyncio.sleep(sleep_interval)

            await websocket.send_text(
                json.dumps({"type": "replay_complete", "mission_id": mission_id})
            )

        except WebSocketDisconnect:
            pass
        finally:
            db.close()

    async def start_constellation_broadcaster(self):
        """Asynchronous background task publishing fleet statuses every 10 seconds."""
        db = TelemetryWarehouse()
        try:
            while True:
                # Query aggregate fleet states
                current_time = datetime.now(timezone.utc).isoformat()

                # Fetch SAT statuses (synthesized nominal aggregates)
                fleet_summary = {
                    "type": "fleet_constellation",
                    "timestamp": current_time,
                    "metrics": {
                        "satellites_online": 10,
                        "anomalies_active": 1,
                        "mean_temp_c": 54.8,
                        "alerts": ["SAT-04 radiator degradation warning active"],
                    },
                }

                await self.publish_redis("fleet", fleet_summary)
                await asyncio.sleep(10.0)
        except asyncio.CancelledError:
            pass
        finally:
            db.close()
