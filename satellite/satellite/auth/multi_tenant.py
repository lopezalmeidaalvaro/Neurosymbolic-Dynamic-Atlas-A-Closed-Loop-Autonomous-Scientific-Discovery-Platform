#!/usr/bin/env python3
"""
Authentication & Multi-Tenant SaaS Interface (T53)
Autonomous Spacecraft Thermal OS
Provides JWT exchanges, bcrypt password hashing, RBAC (admin/member/viewer),
and Redis quota usage tracking with SQLite fallbacks.
"""

import os
import sys
import time
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import Header, Query, HTTPException, status, Depends

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from db.telemetry_warehouse import TelemetryWarehouse

# Environment Configs
SECRET_KEY = os.getenv("SECRET_KEY", "thermal_jwt_secret_token_key_xyz789")
ALGORITHM = "HS256"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis Quota Client setup with SQLite in-memory fallback
try:
    import redis

    redis_client = redis.from_url(REDIS_URL, socket_connect_timeout=2)
    redis_client.ping()
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False
    in_memory_quota = {}  # Fallback in-memory quota: org_id -> count


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=8))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials token.",
        )


# Quota Limit Manager
def check_tenant_quota(org_id: str, plan: str, limit: int) -> int:
    """Checks and increments Org quota usage in Redis with standard fallback."""
    current_month = datetime.now().strftime("%Y-%m")
    quota_key = f"quota:{org_id}:{current_month}"

    if HAS_REDIS:
        try:
            usage = redis_client.get(quota_key)
            if usage is None:
                redis_client.set(quota_key, 0, ex=31 * 24 * 3600)  # 31 days TTL
                usage = 0
            else:
                usage = int(usage)

            if usage >= limit and plan != "enterprise":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Monthly simulation quota limit exceeded ({usage}/{limit}). Upgrade Org subscription to Enterprise.",
                )

            # Increment quota count
            redis_client.incr(quota_key)
            return usage + 1
        except redis.RedisError:
            pass  # Gracefully degrade to memory check if Redis drops

    # In-memory Quota fallback
    usage = in_memory_quota.get(quota_key, 0)
    if usage >= limit and plan != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly simulation quota limit exceeded ({usage}/{limit}).",
        )
    in_memory_quota[quota_key] = usage + 1
    return usage + 1


# Dependency: Verify API Key or Token (RBAC & Quotas)
def get_current_user_tenant(
    x_api_key: str = Header(None),
    api_key: str = Query(None),
    authorization: str = Header(None),
):
    key = x_api_key or api_key
    token = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not key and not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Set X-API-Key / api_key query, or Bearer Authorization token.",
        )

    db = TelemetryWarehouse()

    # CASE 1: Token Authentication (JWT)
    if token:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            db.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token details.",
            )

        if db.use_postgres:
            sql = """
            SELECT u.email, u.role, o.id, o.plan, o.quota_limit 
            FROM users u 
            JOIN organizations o ON u.org_id = o.id 
            WHERE u.id = %s
            """
            cursor = db.execute_sql(sql, (user_id,))
        else:
            sql = """
            SELECT u.email, u.role, o.id, o.plan, o.quota_limit 
            FROM users u 
            JOIN organizations o ON u.org_id = o.id 
            WHERE u.id = ?
            """
            cursor = db.execute_sql(sql, (str(user_id),))

        user = cursor.fetchone()
        db.close()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
            )

        email, role, org_id, plan, quota_limit = user
        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "org_id": org_id,
            "plan": plan,
            "quota_limit": quota_limit,
        }

    # CASE 2: Key Authentication
    if key:
        if db.use_postgres:
            sql = """
            SELECT u.id, u.email, u.role, o.id, o.plan, o.quota_limit 
            FROM api_keys k
            JOIN users u ON k.user_id = u.id
            JOIN organizations o ON u.org_id = o.id
            WHERE k.key_hash = %s AND k.revoked = FALSE
            """
            cursor = db.execute_sql(sql, (key,))
        else:
            sql = """
            SELECT u.id, u.email, u.role, o.id, o.plan, o.quota_limit 
            FROM api_keys k
            JOIN users u ON k.user_id = u.id
            JOIN organizations o ON u.org_id = o.id
            WHERE k.key_hash = ? AND k.revoked = 0
            """
            cursor = db.execute_sql(sql, (str(key),))

        user = cursor.fetchone()
        db.close()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or revoked API Key.",
            )

        u_id, email, role, org_id, plan, quota_limit = user
        return {
            "user_id": u_id,
            "email": email,
            "role": role,
            "org_id": org_id,
            "plan": plan,
            "quota_limit": quota_limit,
            "api_key": key,
        }


# RBAC Gatekeeper Helpers
def verify_role_member_or_admin(user=Depends(get_current_user_tenant)):
    if user["role"] not in ["admin", "member"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation unauthorized. 'viewer' accounts are limited to read-only views.",
        )
    return user


def verify_role_admin(user=Depends(get_current_user_tenant)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation unauthorized. Administrative role permissions required.",
        )
    return user
