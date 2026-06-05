import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class MotifKnowledgeGraph:
    def __init__(self) -> None:
        self.motifs: Dict[str, Dict[str, Any]] = {}

    def add_motif(
        self,
        motif: Dict[str, Any],
        circuit_family: str = "unknown",
        topology: str = "unknown",
        hardware: str = "unknown",
    ) -> None:
        motif_id = motif["motif_id"]
        if motif_id not in self.motifs:
            stored = dict(motif)
            stored["families"] = {}
            stored["topologies"] = {}
            stored["hardware"] = {}
            stored["observations"] = 0
            self.motifs[motif_id] = stored
        stored = self.motifs[motif_id]
        stored["observations"] += int(motif.get("frequency", 1))
        stored["families"][circuit_family] = stored["families"].get(circuit_family, 0) + 1
        stored["topologies"][topology] = stored["topologies"].get(topology, 0) + 1
        stored["hardware"][hardware] = stored["hardware"].get(hardware, 0) + 1
        for key in ("gate_reduction", "depth_reduction", "duration_reduction", "fidelity_gain"):
            old = float(stored.get(key, 0.0))
            new = float(motif.get(key, 0.0))
            n = max(1, stored["observations"])
            stored[key] = old + (new - old) / n

    def add_many(
        self,
        motifs: List[Dict[str, Any]],
        circuit_family: str = "unknown",
        topology: str = "unknown",
        hardware: str = "unknown",
    ) -> None:
        for motif in motifs:
            self.add_motif(motif, circuit_family, topology, hardware)

    def records(self) -> List[Dict[str, Any]]:
        records = []
        for motif in self.motifs.values():
            record = dict(motif)
            record["average_gain"] = (
                float(record.get("gate_reduction", 0.0))
                + float(record.get("depth_reduction", 0.0))
                + float(record.get("duration_reduction", 0.0))
                + 1000.0 * float(record.get("fidelity_gain", 0.0))
            )
            record["confidence_score"] = min(1.0, record.get("observations", 0) / 10.0)
            record["families"] = json.dumps(record.get("families", {}), sort_keys=True)
            record["topologies"] = json.dumps(record.get("topologies", {}), sort_keys=True)
            record["hardware"] = json.dumps(record.get("hardware", {}), sort_keys=True)
            record["pattern_before"] = json.dumps(record.get("pattern_before", []), sort_keys=True)
            record["pattern_after"] = json.dumps(record.get("pattern_after", []), sort_keys=True)
            records.append(record)
        return records

    def persist(self, json_path: Path, csv_path: Path) -> None:
        json_path.parent.mkdir(exist_ok=True)
        csv_path.parent.mkdir(exist_ok=True)
        json_path.write_text(
            json.dumps(list(self.motifs.values()), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        records = self.records()
        if not records:
            csv_path.write_text("", encoding="utf-8")
            return
        fieldnames = sorted(records[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    @classmethod
    def load(cls, json_path: Path) -> "MotifKnowledgeGraph":
        graph = cls()
        if json_path.exists():
            motifs = json.loads(json_path.read_text(encoding="utf-8"))
            graph.motifs = {motif["motif_id"]: motif for motif in motifs}
        return graph
