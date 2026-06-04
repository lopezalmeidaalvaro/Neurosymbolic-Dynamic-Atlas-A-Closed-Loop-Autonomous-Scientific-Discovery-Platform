import os
import sqlite3
import pytest
from quantum.reality_native.prediction_locking_engine import PredictionLockingEngine

@pytest.fixture
def temp_reality_db(tmp_path):
    return str(tmp_path / "test_locking.db")

def test_prediction_locking_flow(temp_reality_db):
    engine = PredictionLockingEngine(reality_db_path=temp_reality_db)
    
    test_preds = [
        {
            "id": "LOCK_TEST_001",
            "theory_id": "RTHEORY_001",
            "predicted_val": 0.355102,
            "condition": {"device": "superconducting_odin", "gate_error": 0.005, "readout_error": 0.010}
        }
    ]
    
    # 1. Lock a new prediction
    records = engine.lock_predictions(test_preds)
    assert len(records) == 1
    assert records[0]["status"] == "NEW_LOCKED"
    assert len(records[0]["checksum"]) == 64  # SHA-256 length
    
    # Verify in DB
    conn = sqlite3.connect(temp_reality_db)
    c = conn.cursor()
    c.execute("SELECT id, predicted_val, checksum FROM locked_predictions WHERE id = 'LOCK_TEST_001'")
    row = c.fetchone()
    assert row is not None
    assert abs(row[1] - 0.355102) < 1e-6
    assert row[2] == records[0]["checksum"]
    conn.close()

    # 2. Attempt to lock again with a modified value (mutation prevention)
    test_preds_modified = [
        {
            "id": "LOCK_TEST_001",
            "theory_id": "RTHEORY_001",
            "predicted_val": 0.999999,  # modified value
            "condition": {"device": "superconducting_odin", "gate_error": 0.005, "readout_error": 0.010}
        }
    ]
    records_retry = engine.lock_predictions(test_preds_modified)
    assert len(records_retry) == 1
    assert records_retry[0]["status"] == "LOCKED_PREVENTED_MUTATION"
    # Ensure value inside DB remains unchanged
    conn = sqlite3.connect(temp_reality_db)
    c = conn.cursor()
    c.execute("SELECT predicted_val FROM locked_predictions WHERE id = 'LOCK_TEST_001'")
    row = c.fetchone()
    assert abs(row[0] - 0.355102) < 1e-6
    conn.close()
