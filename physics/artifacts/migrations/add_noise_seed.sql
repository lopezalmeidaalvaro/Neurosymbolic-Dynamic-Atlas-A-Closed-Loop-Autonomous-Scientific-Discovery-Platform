-- ============================================================
-- migrations/add_noise_seed.sql
-- Phase 3.3B — Persistence & Scientific Consistency Audit
--
-- Idempotent migration: adds noise_level and seed columns to
-- the structural_embeddings table if they are not already present.
--
-- SQLite does not support IF NOT EXISTS on ALTER TABLE.
-- Run each ALTER TABLE separately; ignore "duplicate column" errors
-- (they are expected on repeated runs).
--
-- Verified against real schema (2026-05-20):
--   CREATE TABLE structural_embeddings (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     node_id INTEGER,
--     system_name TEXT,
--     lyapunov_max REAL, spectral_entropy REAL, dominant_frequency REAL,
--     variance REAL, autocorr_decay REAL, kurtosis REAL, skewness REAL,
--     energy REAL, embedding_json TEXT,
--     [noise_level REAL DEFAULT 0.0],   -- added by this migration
--     [seed       REAL DEFAULT 42]      -- added by this migration
--   )
--
-- Columns noise_level and seed have type REAL (not INTEGER for seed)
-- because ALTER TABLE via Python used REAL DEFAULT 42.
-- This is intentional — SQLite stores all numeric types as REAL when
-- declared REAL, but comparisons with integer literals still work.
--
-- RECOMMENDED: after running this migration, create an index to make
-- the (system_name, noise_level, seed) lookup fast under parallel load.
-- ============================================================

-- Step 1: Add noise_level column (no-op if already present)
ALTER TABLE structural_embeddings ADD COLUMN noise_level REAL DEFAULT 0.0;

-- Step 2: Add seed column (no-op if already present)
ALTER TABLE structural_embeddings ADD COLUMN seed REAL DEFAULT 42;

-- Step 3: Backfill existing rows that have NULL in the new columns
-- (rows inserted by the old schema before migration)
UPDATE structural_embeddings
   SET noise_level = 0.0
 WHERE noise_level IS NULL;

UPDATE structural_embeddings
   SET seed = 42
 WHERE seed IS NULL;

-- ============================================================
-- OPTIONAL: Create a covering index for fast (system, noise, seed) lookups
-- Uncomment and run once to improve parallel sweep performance.
-- ============================================================
-- CREATE INDEX IF NOT EXISTS idx_embeddings_key
--   ON structural_embeddings (system_name, noise_level, seed);

-- ============================================================
-- VERIFICATION QUERY — run after migration to confirm columns:
-- ============================================================
-- PRAGMA table_info(structural_embeddings);
-- Expected output includes:
--   12  noise_level  REAL  0  0.0  0
--   13  seed         REAL  0  42   0
