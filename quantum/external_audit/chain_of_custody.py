import os
import sqlite3
import hashlib
from typing import Dict, Any, List

class ChainOfCustodyVerifier:
    """
    Phase X-B: Chain of Custody Verification.
    Audits the integrity of physical files, database referential sanity,
    verifies checksums against manifest, and checks for orphans/broken links.
    """

    def __init__(self, project_root: str, manifest: Dict[str, Any]):
        self.project_root = project_root
        self.manifest = manifest

    def verify(self) -> Dict[str, Any]:
        results = {
            "checksum_integrity": True,
            "sqlite_integrity": True,
            "no_orphan_entries": True,
            "no_broken_references": True,
            "details": [],
            "verdict": "PASS"
        }

        # 1. Checksum Verification
        manifest_records = {r["filepath"]: r["checksum"] for r in self.manifest["records"]}
        for filepath, expected_hash in manifest_records.items():
            full_path = os.path.join(self.project_root, filepath)
            if not os.path.exists(full_path):
                results["checksum_integrity"] = False
                results["details"].append(f"Missing file: {filepath}")
                continue
            
            # calculate hash
            sha256 = hashlib.sha256()
            with open(full_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256.update(byte_block)
            curr_hash = sha256.hexdigest()

            if curr_hash != expected_hash:
                results["checksum_integrity"] = False
                results["details"].append(f"Checksum mismatch for {filepath}: Expected {expected_hash}, got {curr_hash}")

        # 2. SQLite Integrity Check
        db_files = [r["filepath"] for r in self.manifest["records"] if r["filepath"].endswith(".db")]
        for db in db_files:
            full_path = os.path.join(self.project_root, db)
            try:
                conn = sqlite3.connect(full_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                res = cursor.fetchone()[0]
                conn.close()
                if res != "ok":
                    results["sqlite_integrity"] = False
                    results["details"].append(f"SQLite integrity check failed for {db}: {res}")
            except Exception as e:
                results["sqlite_integrity"] = False
                results["details"].append(f"Could not open/verify SQLite DB {db}: {str(e)}")

        # 3. Orphan and Broken Reference Check
        # Connect to main databases and check foreign key constraints or manual references
        theory_path = os.path.join(self.project_root, "theory_memory.db")
        if os.path.exists(theory_path):
            try:
                conn = sqlite3.connect(theory_path)
                cursor = conn.cursor()
                
                # Check predictions refer to existing theories
                cursor.execute("SELECT DISTINCT originating_theory FROM predictions;")
                pred_tids = [r[0] for r in cursor.fetchall() if r[0] is not None]
                
                cursor.execute("SELECT id FROM theories;")
                tids = set([r[0] for r in cursor.fetchall()])
                
                orphans = [tid for tid in pred_tids if tid not in tids]
                if orphans:
                    results["no_orphan_entries"] = False
                    results["details"].append(f"Found {len(orphans)} prediction records referencing non-existent theory IDs in theory_memory.db: {orphans[:5]}")
                conn.close()
            except Exception as e:
                results["no_broken_references"] = False
                results["details"].append(f"Error checking references in theory_memory.db: {str(e)}")

        reality_path = os.path.join(self.project_root, "reality_native.db")
        if os.path.exists(reality_path):
            try:
                conn = sqlite3.connect(reality_path)
                cursor = conn.cursor()
                
                # Check novel_predictions refer to candidate_theories
                cursor.execute("SELECT DISTINCT theory_id FROM novel_predictions WHERE theory_id IS NOT NULL;")
                theory_refs = [r[0] for r in cursor.fetchall()]
                
                cursor.execute("SELECT id FROM candidate_theories;")
                ctheories = set([r[0] for r in cursor.fetchall()])
                
                missing_theories = [t for t in theory_refs if t not in ctheories]
                if missing_theories:
                    results["no_broken_references"] = False
                    results["details"].append(f"Found novel predictions referencing non-existent candidate theories: {missing_theories[:5]}")
                conn.close()
            except Exception as e:
                results["no_broken_references"] = False
                results["details"].append(f"Error checking references in reality_native.db: {str(e)}")

        # Final verdict
        if not (results["checksum_integrity"] and results["sqlite_integrity"] and results["no_orphan_entries"] and results["no_broken_references"]):
            results["verdict"] = "FAIL"

        self._write_report(results)
        return results

    def _write_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Chain of Custody Verification Report -- Phase X-B",
            "",
            f"**Verdict**: **`{results['verdict']}`**",
            "",
            "## Integrity Check Details",
            "",
            f"- **Checksum Integrity**: `{'PASS' if results['checksum_integrity'] else 'FAIL'}`",
            f"- **SQLite Structural Integrity**: `{'PASS' if results['sqlite_integrity'] else 'FAIL'}`",
            f"- **No Orphan Entries**: `{'PASS' if results['no_orphan_entries'] else 'FAIL'}`",
            f"- **No Broken References**: `{'PASS' if results['no_broken_references'] else 'FAIL'}`",
            "",
            "## Detail Logs",
            ""
        ]

        if results["details"]:
            for d in results["details"]:
                lines.append(f"- [ ] {d}")
        else:
            lines.append("- All structural, checksum, and referential checks completed successfully with no anomalies.")

        lines.append("")

        docs_dir = os.path.join(self.project_root, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, "CHAIN_OF_CUSTODY_REPORT.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
