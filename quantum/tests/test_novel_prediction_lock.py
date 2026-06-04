import os
import pytest
from quantum.novel_physics.novel_prediction_lock import NovelPredictionLock

def test_novel_prediction_lock():
    locker = NovelPredictionLock()
    predictions = [
        {"case_id": "IMP_001_00", "theory_id": "RTHEORY_001",
         "standard_prediction": 0.0, "rtheory_prediction": -0.05},
        {"case_id": "IMP_002_00", "theory_id": "RTHEORY_002",
         "standard_prediction": 0.0, "rtheory_prediction": -0.08},
    ]
    locked = locker.lock_predictions(predictions)
    assert locked["status"] == "LOCKED"
    assert len(locked["records"]) == 2
    for r in locked["records"]:
        assert "sha256" in r
        assert len(r["sha256"]) == 64  # SHA-256 hex length
        assert r["frozen_record"]["standard_prediction"] == 0.0
    assert os.path.exists("docs/NOVEL_PREDICTION_LOCK.md")
