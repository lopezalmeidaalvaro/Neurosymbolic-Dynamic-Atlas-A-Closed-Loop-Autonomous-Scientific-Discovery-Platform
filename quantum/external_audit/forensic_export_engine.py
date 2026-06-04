import os
import hashlib
import time
from typing import Dict, Any, List

class ForensicExportEngine:
    """
    Phase X-A: Forensic Export Engine.
    Exports/registers every artifact required for independent verification,
    including theory, discovery, confirmation, reproduction, and Phase 4 databases,
    generating a cryptographic manifest.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root

    def get_audit_db_files(self) -> List[str]:
        # Find databases in root and databases/ directory
        targets = [
            "theory_memory.db",
            "evidence_memory.db",
            "reality_native.db",
            "scientific_kb.db"
        ]
        db_files = []
        for t in targets:
            path = os.path.join(self.project_root, t)
            if os.path.exists(path):
                db_files.append(path)

        # Check databases directory
        db_dir = os.path.join(self.project_root, "databases")
        if os.path.exists(db_dir):
            for f in os.listdir(db_dir):
                if f.endswith(".db"):
                    db_files.append(os.path.join(db_dir, f))
        return db_files

    def calculate_sha256(self, filepath: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_manifest(self) -> Dict[str, Any]:
        db_files = self.get_audit_db_files()
        records = []
        for db in db_files:
            stat = os.stat(db)
            checksum = self.calculate_sha256(db)
            records.append({
                "filepath": os.path.relpath(db, self.project_root),
                "checksum": checksum,
                "size": stat.st_size,
                "created": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(stat.st_ctime)),
                "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(stat.st_mtime))
            })

        manifest = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            "records": records
        }

        self._write_manifest_report(manifest)
        return manifest

    def _write_manifest_report(self, manifest: Dict[str, Any]) -> None:
        lines = [
            "# Forensic Export Manifest -- Phase X-A",
            "",
            f"**Generation Timestamp**: `{manifest['timestamp']} UTC`",
            "",
            "This manifest records all physical database artifacts and locks their cryptographic state to ensure a tamper-proof verification history.",
            "",
            "| File Path | SHA-256 Checksum | File Size (Bytes) | Created Timestamp | Modified Timestamp |",
            "| :--- | :--- | :---: | :--- | :--- |"
        ]

        for r in manifest["records"]:
            lines.append(
                f"| `{r['filepath']}` | `{r['checksum']}` | `{r['size']}` | `{r['created']}` | `{r['modified']}` |"
            )

        lines.append("")
        lines.append(f"- **Total Exported Artifacts**: `{len(manifest['records'])}`")
        lines.append("")

        # Save in docs/
        docs_dir = os.path.join(self.project_root, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, "FORENSIC_EXPORT_MANIFEST.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
