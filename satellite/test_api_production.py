# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - SaaS API Production Test Suite
# File: test_api_production.py
# Description: Asserts endpoint security, JWT validations, quotas and simulator math.
# ==============================================================================

import os
import sys
import unittest
import json
import time
from fastapi.testclient import TestClient

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.thermal_api import app, DB_PATH


class TestSaaSAPIProduction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import sqlite3

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username != 'admin'")
        c.execute("DELETE FROM usage")
        c.execute("DELETE FROM checkout_sessions")
        conn.commit()
        conn.close()
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        """
        TC-API-001: Verifies `/v1/health` status reporting and telemetry logs.
        """
        response = self.client.get("/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("system_telemetry", data)

    def test_metrics_endpoint(self):
        """
        TC-API-002: Verifies Prometheus `/v1/metrics` exporter outputs.
        """
        response = self.client.get("/v1/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("thermal_api_uptime_seconds", response.text)

    def test_user_authentication_workflow(self):
        """
        TC-API-003: Registers a user, logs in to generate a JWT, and routes a secure endpoint.
        """
        import uuid

        username = f"op_{uuid.uuid4().hex[:8]}"
        email = f"{username}@spaceframe.org"

        # 1. Register User
        reg_payload = {
            "username": username,
            "email": email,
            "password": "strongpassword123",
        }
        res_reg = self.client.post("/v1/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 200)
        reg_data = res_reg.json()
        self.assertEqual(reg_data["status"], "success")
        self.assertIn("api_key", reg_data)

        # 2. Login User
        login_payload = {"username": username, "password": "strongpassword123"}
        res_login = self.client.post("/v1/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.json()
        self.assertEqual(login_data["status"], "success")
        self.assertIn("token", login_data)
        token = login_data["token"]

        # 3. Request `/v1/simulate` with JWT Token
        sim_payload = {
            "power": 30.0,
            "area": 0.15,
            "emissivity": 0.85,
            "heat_capacity": 500.0,
            "initial_temp": 25.0,
        }
        headers = {"Authorization": f"Bearer {token}"}
        res_sim = self.client.post("/v1/simulate", json=sim_payload, headers=headers)
        self.assertEqual(res_sim.status_code, 200)
        sim_data = res_sim.json()
        self.assertEqual(sim_data["status"], "success")
        self.assertIn("temperatures", sim_data)

    def test_api_key_authentication_routing(self):
        """
        TC-API-004: Validates `/v1/thermal/predict` utilizing secure Header and Query API keys.
        """
        payload = {"power": 15.0, "area": 0.15, "emissivity": 0.85}

        # Using correct default admin key via header
        headers = {"X-API-Key": "pro_enterprise_key_xyz987"}
        response = self.client.post(
            "/v1/thermal/predict", json=payload, headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("max_temp_c", data)

        # Using incorrect key (must yield 403)
        headers_bad = {"X-API-Key": "invalid_key_xyz"}
        response_bad = self.client.post(
            "/v1/thermal/predict", json=payload, headers=headers_bad
        )
        self.assertEqual(response_bad.status_code, 403)

    def test_fdir_fault_detector_telemetry(self):
        """
        TC-API-005: Verifies `/v1/fault-detect` warns on radiator decays and SEUs.
        """
        headers = {"X-API-Key": "pro_enterprise_key_xyz987"}

        # Nominal case
        nom_payload = {
            "observed_temp": 35.0,
            "calibrated_emissivity": 0.85,
            "bitflip_count": 0,
        }
        res_nom = self.client.post(
            "/v1/fault-detect", json=nom_payload, headers=headers
        )
        self.assertEqual(res_nom.status_code, 200)
        self.assertFalse(res_nom.json()["fault_detected"])

        # Faulty case: Low emissivity + high temp + bitflips
        fault_payload = {
            "observed_temp": 86.2,
            "calibrated_emissivity": 0.35,
            "bitflip_count": 12,
        }
        res_fault = self.client.post(
            "/v1/fault-detect", json=fault_payload, headers=headers
        )
        self.assertEqual(res_fault.status_code, 200)
        data = res_fault.json()
        self.assertTrue(data["fault_detected"])
        self.assertIn("primary_action", data)
        self.assertEqual(len(data["warnings"]), 3)

    def test_mission_planner_thermal_feasibility(self):
        """
        TC-API-006: Verifies `/v1/mission/run` schedules tasks within safe parameters.
        """
        headers = {"X-API-Key": "pro_enterprise_key_xyz987"}
        payload = {
            "tasks": [
                {
                    "name": "Earth_Imaging_Low",
                    "duration": 120.0,
                    "power_draw": 15.0,
                    "priority": 5,
                },
                {
                    "name": "Optics_Saturating_Heavy",
                    "duration": 500.0,
                    "power_draw": 200.0,
                    "priority": 10,
                },
            ]
        }
        response = self.client.post("/v1/mission/run", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Earth_Imaging_Low", data["scheduled_tasks"])
        self.assertIn("Optics_Saturating_Heavy", data["skipped_tasks"])

    def test_telemetry_outlier_cleaner(self):
        """
        TC-API-007: Verifies `/v1/telemetry/analyze` removes spikes and smooths.
        """
        headers = {"X-API-Key": "pro_enterprise_key_xyz987"}
        payload = {"raw_cpu_temperatures": [35.0, 35.5, 75.0, 35.8, 35.2]}
        response = self.client.post(
            "/v1/telemetry/analyze", json=payload, headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLess(data["cleaned_temperatures"][2], 40.0)
        self.assertEqual(len(data["smoothed_temperatures"]), 5)

    def test_stripe_subscription_upgrades(self):
        """
        TC-API-008: Simulates Stripe billing checkouts and webhook profile upgrades.
        """
        # 1. Initiate checkout session
        checkout_payload = {"email": "customer@spaceframe.org", "plan": "Professional"}
        res_check = self.client.post("/v1/stripe/checkout", json=checkout_payload)
        self.assertEqual(res_check.status_code, 200)
        checkout_data = res_check.json()
        self.assertIn("checkout_url", checkout_data)

        # 2. Simulate Stripe Webhook upgrades
        webhook_payload = {
            "type": "charge.succeeded",
            "data": {
                "object": {"billing_details": {"email": "customer@spaceframe.org"}}
            },
        }

        # Register user as free tier first
        reg_payload = {
            "username": "customer_user",
            "email": "customer@spaceframe.org",
            "password": "customerpassword123",
        }
        self.client.post("/v1/auth/register", json=reg_payload)

        res_webhook = self.client.post("/v1/stripe/webhook", json=webhook_payload)
        self.assertEqual(res_webhook.status_code, 200)
        self.assertEqual(res_webhook.json()["status"], "success")


if __name__ == "__main__":
    unittest.main()
