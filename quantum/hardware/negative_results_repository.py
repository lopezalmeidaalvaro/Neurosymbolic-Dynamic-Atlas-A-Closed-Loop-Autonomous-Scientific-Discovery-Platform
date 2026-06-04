import uuid
import time
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class NegativeResultsRepository:
    """
    Component N: Negative Result Preservation.
    Saves failed theories, rejected predictions, and collapsed mechanisms
    to SQL memory to preserve refutations.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)

    def record_failure(self, failure_type: str, target_id: str, reason: str) -> None:
        """
        Saves a failure record to the database negative_results table.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        neg_id = f"NEG_{uuid.uuid4().hex[:8].upper()}"
        
        neg_data = {
            "id": neg_id,
            "type": failure_type, # 'theory', 'prediction', 'mechanism'
            "target_id": target_id,
            "reason": reason,
            "timestamp": timestamp
        }
        
        self.memory.save_negative_result(neg_data)
        print(f"Recorded negative result / refutation: {failure_type.upper()} {target_id} - Reason: {reason[:45]}...")

    def get_failures(self) -> List[Dict[str, Any]]:
        return self.memory.get_all_negative_results()

if __name__ == "__main__":
    repo = NegativeResultsRepository()
    repo.record_failure("theory", "THEORY_999", "Failed replication rate")
    print(repo.get_failures())
