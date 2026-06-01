# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - SaaS API Production Hardening Test Suite
# File: tests/test_api_hardening.py
# Description: Asserts CORS validation, Swagger gating, Rate Limiting and health checks.
# ==============================================================================

import os
import sys
import unittest
import importlib
from fastapi.testclient import TestClient

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAPIHardening(unittest.TestCase):

    def test_dedicated_health_endpoint(self):
        """
        TC-HARD-001: Verifies the dedicated GET `/health` endpoint returns the exact hardened payload.
        """
        from backend.thermal_api import app
        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {
            "status": "ok",
            "service": "AST-OS",
            "version": "3.0.0"
        })

    def test_legacy_health_endpoint(self):
        """
        TC-HARD-002: Verifies that legacy GET `/v1/health` remains fully functional and unaffected.
        """
        from backend.thermal_api import app
        client = TestClient(app)
        response = client.get("/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("system_telemetry", data)

    def test_swagger_suppression_production(self):
        """
        TC-HARD-003: Asserts that when ENV=production, Swagger docs endpoints are disabled (404).
        """
        # Set env var
        os.environ["ENV"] = "production"
        
        # Reload module to apply environment changes
        import backend.thermal_api
        importlib.reload(backend.thermal_api)
        
        client = TestClient(backend.thermal_api.app)
        
        # Check docs
        self.assertEqual(client.get("/docs").status_code, 404)
        self.assertEqual(client.get("/redoc").status_code, 404)
        self.assertEqual(client.get("/openapi.json").status_code, 404)
        
        # Cleanup env var
        del os.environ["ENV"]
        importlib.reload(backend.thermal_api)

    def test_swagger_enabled_development(self):
        """
        TC-HARD-004: Asserts that when ENV is not production (default), docs endpoints are enabled (200).
        """
        if "ENV" in os.environ:
            del os.environ["ENV"]
            
        import backend.thermal_api
        importlib.reload(backend.thermal_api)
        
        client = TestClient(backend.thermal_api.app)
        
        self.assertEqual(client.get("/docs").status_code, 200)
        self.assertEqual(client.get("/redoc").status_code, 200)
        self.assertEqual(client.get("/openapi.json").status_code, 200)

    def test_cors_parsing_origins(self):
        """
        TC-HARD-005: Asserts that CORS middleware processes custom ALLOWED_ORIGINS dynamically.
        """
        os.environ["ALLOWED_ORIGINS"] = "https://custom-dashboard.spaceframe.org, https://ast-os.com"
        
        import backend.thermal_api
        importlib.reload(backend.thermal_api)
        
        client = TestClient(backend.thermal_api.app)
        
        # Test default permitted origin
        headers_default = {
            "Origin": "https://autonomous-spacecraft-thermal-os.onrender.com",
            "Access-Control-Request-Method": "GET"
        }
        res_def = client.options("/health", headers=headers_default)
        self.assertEqual(res_def.headers.get("access-control-allow-origin"), "https://autonomous-spacecraft-thermal-os.onrender.com")

        # Test first custom origin
        headers_custom1 = {
            "Origin": "https://custom-dashboard.spaceframe.org",
            "Access-Control-Request-Method": "GET"
        }
        res_cust1 = client.options("/health", headers=headers_custom1)
        self.assertEqual(res_cust1.headers.get("access-control-allow-origin"), "https://custom-dashboard.spaceframe.org")

        # Test second custom origin
        headers_custom2 = {
            "Origin": "https://ast-os.com",
            "Access-Control-Request-Method": "GET"
        }
        res_cust2 = client.options("/health", headers=headers_custom2)
        self.assertEqual(res_cust2.headers.get("access-control-allow-origin"), "https://ast-os.com")

        # Test unauthorized origin
        headers_unauth = {
            "Origin": "https://unauthorized-hacker-domain.com",
            "Access-Control-Request-Method": "GET"
        }
        res_unauth = client.options("/health", headers=headers_unauth)
        self.assertIsNone(res_unauth.headers.get("access-control-allow-origin"))

        # Cleanup env
        del os.environ["ALLOWED_ORIGINS"]
        importlib.reload(backend.thermal_api)

    def test_rate_limiting_slowapi(self):
        """
        TC-HARD-006: Verifies that SlowAPI rate limiting triggers 429 Too Many Requests after limit.
        """
        import backend.thermal_api
        importlib.reload(backend.thermal_api)
        
        client = TestClient(backend.thermal_api.app)
        
        # We target `/v1/public/metrics` which has a limit of 100/minute.
        # We will make 100 successful requests and then assert the 101st request is blocked with HTTP 429.
        for i in range(100):
            res = client.get("/v1/public/metrics")
            self.assertEqual(res.status_code, 200, f"Request {i} failed prematurely")
            
        # The 101st request should be blocked by rate limit
        res_blocked = client.get("/v1/public/metrics")
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Rate limit exceeded", res_blocked.json()["error"])

if __name__ == "__main__":
    unittest.main()
