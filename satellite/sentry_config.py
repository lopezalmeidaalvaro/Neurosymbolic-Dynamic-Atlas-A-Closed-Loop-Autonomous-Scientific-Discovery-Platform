# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - Sentry Error Tracking Config
# File: sentry_config.py
# Description: Initializes Sentry SDK with standard settings for production APIs.
# ==============================================================================

import os
import logging

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastAPIIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    HAS_SENTRY = True
except ImportError:
    HAS_SENTRY = False


def init_sentry(app=None):
    """
    Initializes Sentry for the FastAPI app using production environments.
    """
    sentry_dsn = os.getenv(
        "SENTRY_DSN", "https://mock_sentry_dsn_key@o450.ingest.sentry.io/4509"
    )
    environment = os.getenv("ENVIRONMENT", "production")

    if not HAS_SENTRY:
        print(
            "[*] Sentry SDK not installed. Skipping telemetry error tracking initialization."
        )
        return False

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=[FastAPIIntegration(), sentry_logging],
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile transactions
        profiles_sample_rate=1.0,
        send_default_pii=True,
    )

    print(
        f"[+] Sentry successfully initialized error tracking under environment: '{environment}'"
    )
    return True


if __name__ == "__main__":
    init_sentry()
