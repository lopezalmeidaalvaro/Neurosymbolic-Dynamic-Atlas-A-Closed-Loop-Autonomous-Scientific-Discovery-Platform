-- PostgreSQL / TimescaleDB Database Initialization Schema
-- Autonomous Spacecraft Thermal OS

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable TimescaleDB extension if available (graceful degradation if standard PG)
DO $$
BEGIN
    PERFORM * FROM pg_extension WHERE extname = 'timescaledb';
    IF NOT FOUND THEN
        BEGIN
            CREATE EXTENSION timescaledb CASCADE;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'TimescaleDB extension not found. Proceeding with standard PostgreSQL tables.';
        END;
    END IF;
END $$;

-- =============================================================================
-- SaaS MULTI-TENANT STRUCTURES (T53)
-- =============================================================================

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    plan VARCHAR(50) DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    quota_limit INTEGER DEFAULT 100, -- Monthly simulation quota limit
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'viewer', -- 'admin', 'member', 'viewer'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMPTZ,
    revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS waitlist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    company VARCHAR(255),
    use_case TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- MISSION CORE STRUCTURES (T52)
-- =============================================================================

CREATE TABLE IF NOT EXISTS missions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    satellite_id VARCHAR(100) NOT NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    start_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMPTZ,
    orbit_params JSONB NOT NULL -- Altitude, eclipse, initial beta values
);

CREATE INDEX IF NOT EXISTS idx_missions_satellite_start 
ON missions(satellite_id, start_time);

-- =============================================================================
-- TELEMETRY TIMESERIES TIMESCALEDB HYPERTABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS telemetry (
    time TIMESTAMPTZ NOT NULL,
    mission_id UUID REFERENCES missions(id) ON DELETE CASCADE,
    node_id VARCHAR(50) NOT NULL, -- 'CPU', 'Battery', 'Payload', 'Structure', 'Radiator', 'SolarPanels'
    temperature DOUBLE PRECISION NOT NULL,
    power DOUBLE PRECISION NOT NULL,
    radiator_state DOUBLE PRECISION, -- Current emissivity twin parameter
    anomaly_flags TEXT[] -- Null or active alerts ['CPU_EXCEEDANCE', 'RADIATOR_DEGRADATION']
);

-- Partition telemetry as timeseries hypertable (1-day chunk intervals)
DO $$
BEGIN
    IF EXISTS (SELECT * FROM pg_proc WHERE proname = 'create_hypertable') THEN
        PERFORM create_hypertable('telemetry', 'time', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Skipping TimescaleDB hypertable creation (using standard PG timeseries partitioning).';
END $$;

CREATE INDEX IF NOT EXISTS idx_telemetry_mission_time 
ON telemetry(mission_id, time DESC);

-- =============================================================================
-- EKF PARAMETERS STATE VECTORS REGISTRY
-- =============================================================================

CREATE TABLE IF NOT EXISTS ekf_history (
    time TIMESTAMPTZ NOT NULL,
    mission_id UUID REFERENCES missions(id) ON DELETE CASCADE,
    state_vector DOUBLE PRECISION[] NOT NULL, -- Augmented EKF [T0..T5, emissivity]
    covariance_matrix DOUBLE PRECISION[] NOT NULL, -- Flattened P covariance matrix
    innovation DOUBLE PRECISION, -- Innovation residuals
    status VARCHAR(50) DEFAULT 'nominal' -- 'nominal', 'calibrating', 'diverging'
);

-- Partition EKF History as timeseries hypertable
DO $$
BEGIN
    IF EXISTS (SELECT * FROM pg_proc WHERE proname = 'create_hypertable') THEN
        PERFORM create_hypertable('ekf_history', 'time', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        NULL;
END $$;

CREATE INDEX IF NOT EXISTS idx_ekf_mission_time 
ON ekf_history(mission_id, time DESC);

-- =============================================================================
-- ANOMALY & CONTROLS AUDIT LOGGER
-- =============================================================================

CREATE TABLE IF NOT EXISTS anomaly_logs (
    time TIMESTAMPTZ NOT NULL,
    mission_id UUID REFERENCES missions(id) ON DELETE CASCADE,
    anomaly_type VARCHAR(100) NOT NULL, -- 'RADIATOR_DEGRADATION', 'SENSORS_DRIFT'
    severity VARCHAR(50) NOT NULL, -- 'warning', 'critical'
    description TEXT,
    action_taken TEXT, -- 'CPU_THROTTLING_ACTIVE', 'PAYLOAD_SUSPENDED'
    resolved BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_anomalies_mission_time 
ON anomaly_logs(mission_id, time DESC);

-- =============================================================================
-- NEUROSYMBOLIC EQUATION DISCOVERIES REGISTRY
-- =============================================================================

CREATE TABLE IF NOT EXISTS symbolic_discoveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mission_id UUID REFERENCES missions(id) ON DELETE CASCADE,
    equation_latex VARCHAR(512) NOT NULL,
    complexity INTEGER NOT NULL,
    r2_score DOUBLE PRECISION NOT NULL,
    patentability_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- BOOTSTRAP PROFILES FOR LOCAL TEST SUITES
-- =============================================================================

INSERT INTO organizations (id, name, plan, quota_limit) 
VALUES ('c4b8e212-0000-4000-a000-000000000001', 'ESA NewSpace Incubator', 'pro', 1000)
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (id, email, hashed_password, org_id, role)
VALUES (
    'u4b8e212-0000-4000-a000-000000000001', 
    'mission-director@esa-bic.org', 
    '$2b$12$V.oAasq36/6f7Zg6PjSw8OVt/Vv.qj3Lq/V/Sw4HwG0uW5SwXfG6u', -- 'password123' bcrypt
    'c4b8e212-0000-4000-a000-000000000001', 
    'admin'
)
ON CONFLICT (email) DO NOTHING;

-- Insert local default API keys matching standard LOCAL TEST KEYS
INSERT INTO api_keys (id, key_hash, user_id, revoked)
VALUES (
    'k4b8e212-0000-4000-a000-000000000001',
    'pro_enterprise_key_xyz987', -- Pre-hashed or exact matching
    'u4b8e212-0000-4000-a000-000000000001',
    FALSE
)
ON CONFLICT (key_hash) DO NOTHING;
