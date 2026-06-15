from mathematics.knowledge_base.library_manager import FormalKnowledgeBase


class TrajectoryAnalytics:
    """Extracts curriculum performance metrics from SQLite using JSON queries."""

    def __init__(self, kb: FormalKnowledgeBase) -> None:
        self.kb = kb

    def get_success_rate_by_difficulty(self) -> dict:
        """Computes total attempts and success rates grouped by curriculum difficulty level."""
        conn = self.kb._connect()
        try:
            query = """
                SELECT 
                    json_extract(metadata, '$.difficulty') AS difficulty,
                    COUNT(*) AS total_attempts,
                    SUM(CASE WHEN status = 'VERIFIED' THEN 1 ELSE 0 END) AS successes
                FROM proof_trajectories
                WHERE metadata IS NOT NULL 
                  AND json_extract(metadata, '$.difficulty') IS NOT NULL
                GROUP BY difficulty
            """
            rows = conn.execute(query).fetchall()
            result = {}
            for r in rows:
                diff = r["difficulty"]
                try:
                    diff_key = int(diff)
                except (ValueError, TypeError):
                    diff_key = diff

                total = r["total_attempts"]
                successes = r["successes"]
                success_rate = (successes / total) if total > 0 else 0.0

                result[diff_key] = {
                    "total_attempts": total,
                    "success_rate": success_rate,
                }
            return result
        finally:
            conn.close()

    def get_metrics_by_family(self) -> dict:
        """Computes execution count, success rate, and average reward grouped by motif family."""
        conn = self.kb._connect()
        try:
            query = """
                SELECT 
                    json_extract(metadata, '$.family') AS family,
                    COUNT(*) AS total_attempts,
                    SUM(CASE WHEN status = 'VERIFIED' THEN 1 ELSE 0 END) AS successes,
                    AVG(reward) AS avg_reward
                FROM proof_trajectories
                WHERE metadata IS NOT NULL 
                  AND json_extract(metadata, '$.family') IS NOT NULL
                GROUP BY family
            """
            rows = conn.execute(query).fetchall()
            result = {}
            for r in rows:
                fam = r["family"]
                total = r["total_attempts"]
                successes = r["successes"]
                avg_reward = r["avg_reward"]
                success_rate = (successes / total) if total > 0 else 0.0

                result[fam] = {
                    "total_attempts": total,
                    "success_rate": success_rate,
                    "avg_reward": avg_reward if avg_reward is not None else 0.0,
                }
            return result
        finally:
            conn.close()

    def get_metrics_by_proof_origin(self) -> dict:
        """Computes execution count, success rate, and average reward grouped by proof origin."""
        conn = self.kb._connect()
        try:
            query = """
                SELECT 
                    json_extract(metadata, '$.proof_origin') AS proof_origin,
                    COUNT(*) AS total_attempts,
                    SUM(CASE WHEN status = 'VERIFIED' THEN 1 ELSE 0 END) AS successes,
                    AVG(reward) AS avg_reward
                FROM proof_trajectories
                WHERE metadata IS NOT NULL 
                  AND json_extract(metadata, '$.proof_origin') IS NOT NULL
                GROUP BY proof_origin
            """
            rows = conn.execute(query).fetchall()
            result = {}
            for r in rows:
                origin = r["proof_origin"]
                total = r["total_attempts"]
                successes = r["successes"]
                avg_reward = r["avg_reward"]
                success_rate = (successes / total) if total > 0 else 0.0

                result[origin] = {
                    "total_attempts": total,
                    "success_rate": success_rate,
                    "avg_reward": avg_reward if avg_reward is not None else 0.0,
                }
            return result
        finally:
            conn.close()
