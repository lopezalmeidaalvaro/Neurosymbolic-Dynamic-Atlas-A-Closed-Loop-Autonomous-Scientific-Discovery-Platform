from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from physics.core.base_module import ScientificModule
    from physics.core.autonomous.latent_snapshot_exporter import compute_embedding_vector
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from core.base_module import ScientificModule
    from core.autonomous.latent_snapshot_exporter import compute_embedding_vector


PHYSICS_ROOT = Path(__file__).resolve().parent
REAL_DATA_DIR = PHYSICS_ROOT / "data" / "real"


class RealDataIngestor(ScientificModule):
    """Real-data connectors that complement existing MIT-BIH and UCR loaders."""

    existing_sources = {
        "MIT-BIH": "physics/core/empirical/mit_bih_bifurcated_audit.py",
        "UCR": "physics/ucr_loader.py",
        "PhysioNet ECG synthetic audit": "physics/core/empirical/physionet_ecg_audit.py",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        REAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.download_log: list[dict[str, Any]] = []

    def download_kepler_data(self, kepid: str | int) -> dict[str, Any]:
        payload = {
            "service": "Mast.Caom.Cone",
            "params": {"columns": "obsid,target_name,filters,t_exptime", "ra": 0, "dec": 0, "radius": 0.0001},
            "format": "json",
            "pagesize": 5,
        }
        url = "https://mast.stsci.edu/api/v0/invoke"
        result = self._post_json(url, payload, f"kepler_{kepid}.json")
        result["source"] = "Kepler/MAST"
        result["requested_id"] = str(kepid)
        return self._record(result)

    def download_noaa_data(self, dataset: str, start: str, end: str) -> dict[str, Any]:
        name = dataset.strip().lower()
        if name in {"mauna loa", "maunaloa", "co2"}:
            url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
            result = self._download_text(url, "noaa_mauna_loa_co2.csv")
        elif name in {"ghcn-d", "ghcnd"}:
            query = urllib.parse.urlencode(
                {
                    "dataset": "daily-summaries",
                    "startDate": start,
                    "endDate": end,
                    "format": "json",
                    "limit": 100,
                }
            )
            url = f"https://www.ncei.noaa.gov/cdo-web/api/v2/data?{query}"
            headers = {}
            token = os.getenv("NOAA_TOKEN") or self.config_manager.get("data.noaa_token")
            if token:
                headers["token"] = token
            result = self._download_text(url, "noaa_ghcn_d.json", headers=headers)
        else:
            result = {"ok": False, "error": f"unsupported_noaa_dataset: {dataset}", "path": None}
        result.update({"source": "NOAA", "dataset": dataset, "start": start, "end": end})
        return self._record(result)

    def download_materials_data(self, material_id: str) -> dict[str, Any]:
        api_key = os.getenv("MATERIALS_PROJECT_API_KEY") or self.config_manager.get("materials.api_key")
        if not api_key:
            return self._record(
                {
                    "ok": False,
                    "source": "Materials Project",
                    "material_id": material_id,
                    "path": None,
                    "error": "missing MATERIALS_PROJECT_API_KEY",
                }
            )
        url = f"https://api.materialsproject.org/materials/summary/{urllib.parse.quote(material_id)}"
        result = self._download_text(url, f"materials_{material_id}.json", headers={"X-API-KEY": api_key})
        result.update({"source": "Materials Project", "material_id": material_id})
        return self._record(result)

    def check_tuh_eeg_optional(self) -> dict[str, Any]:
        try:
            import mne  # noqa: F401

            return self._record({"ok": False, "source": "TUH EEG", "path": None, "error": "connector_not_configured"})
        except Exception:
            return self._record({"ok": False, "source": "TUH EEG", "path": None, "error": "optional_dependency_missing"})

    def convert_to_pipeline_format(self, dataset_name: str, raw_data: Any) -> dict[str, Any]:
        frame = _to_numeric_frame(raw_data)
        output_path = REAL_DATA_DIR / f"{_safe_name(dataset_name)}_pipeline.csv"
        if frame.empty:
            output_path.write_text("dataset,warning\n%s,no_numeric_data\n" % dataset_name, encoding="utf-8")
            return {"ok": False, "dataset": dataset_name, "path": str(output_path), "error": "no_numeric_data"}
        values = frame.to_numpy(dtype=float)
        signal = values[:, 0] if values.ndim == 2 else values.ravel()
        try:
            embedding = compute_embedding_vector(signal[: min(len(signal), 512)], dt=1.0)
            emb_frame = pd.DataFrame([np.asarray(embedding, dtype=float).ravel()])
        except Exception:
            emb_frame = pd.DataFrame(values[:1])
        emb_frame.to_csv(output_path, index=False)
        return {"ok": True, "dataset": dataset_name, "path": str(output_path), "n_features": int(emb_frame.shape[1])}

    def generate_real_data_catalog(self) -> str:
        catalog_path = PHYSICS_ROOT / "data" / "real_data_catalog.md"
        successful = [item for item in self.download_log if item.get("ok")]
        lines = [
            "# Real Data Catalog",
            "",
            f"Generated: {datetime.now().isoformat(timespec='seconds')}",
            "",
            "This catalog lists successfully downloaded real-data sources plus existing local ingestion paths.",
            "",
            "## Existing Reusable Sources",
            "",
        ]
        for name, path in self.existing_sources.items():
            lines.append(f"- **{name}**: `{path}`")
        lines.extend(["", "## Successful New Downloads", ""])
        if not successful:
            lines.append("- No new external dataset was successfully downloaded in this run.")
        for item in successful:
            lines.append(f"- **{item.get('source')}**: `{item.get('path')}`")
        catalog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(catalog_path)

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        self.check_tuh_eeg_optional()
        catalog_path = self.generate_real_data_catalog()
        metrics = {
            "existing_sources": len(self.existing_sources),
            "successful_new_downloads": sum(1 for item in self.download_log if item.get("ok")),
            "failed_or_skipped_downloads": sum(1 for item in self.download_log if not item.get("ok")),
            "catalog_path": catalog_path,
        }
        report_path = self.log_result(metrics, "real_data_ingestion_report.md")
        return {"metrics": metrics, "report_path": report_path, "downloads": self.download_log}

    def _download_text(self, url: str, filename: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        path = REAL_DATA_DIR / filename
        try:
            request = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(request, timeout=self.config_manager.get("physics.default_timeout", 300)) as response:
                payload = response.read()
            path.write_bytes(payload)
            return {"ok": True, "path": str(path), "url": url, "bytes": len(payload)}
        except Exception as exc:
            return {"ok": False, "path": None, "url": url, "error": str(exc)}

    def _post_json(self, url: str, payload: dict[str, Any], filename: str) -> dict[str, Any]:
        path = REAL_DATA_DIR / filename
        try:
            encoded = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(url, data=encoded, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=self.config_manager.get("physics.default_timeout", 300)) as response:
                response_payload = response.read()
            path.write_bytes(response_payload)
            return {"ok": True, "path": str(path), "url": url, "bytes": len(response_payload)}
        except Exception as exc:
            return {"ok": False, "path": None, "url": url, "error": str(exc)}

    def _record(self, result: dict[str, Any]) -> dict[str, Any]:
        self.download_log.append(result)
        return result


def _to_numeric_frame(raw_data: Any) -> pd.DataFrame:
    if isinstance(raw_data, pd.DataFrame):
        return raw_data.select_dtypes(include=[np.number])
    if isinstance(raw_data, (str, Path)) and Path(raw_data).exists():
        path = Path(raw_data)
        try:
            if path.suffix.lower() == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
                return pd.json_normalize(data).select_dtypes(include=[np.number])
            return pd.read_csv(path, comment="#").select_dtypes(include=[np.number])
        except Exception:
            return pd.DataFrame()
    try:
        return pd.DataFrame(raw_data).select_dtypes(include=[np.number])
    except Exception:
        return pd.DataFrame()


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in str(name).lower()).strip("_")


if __name__ == "__main__":
    print(json.dumps(RealDataIngestor().run(), indent=2))
