import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ResearchRegistry:
    """
    Unified Experiment Registry. Centralizes all scientific findings across 
    quantum simulation, symbolic optimization, noise resilience, QML, and transferability.
    """

    def __init__(self, filename: str = "research_registry.json"):
        self.filename = filename
        self.registry: Dict[str, List[Dict[str, Any]]] = {
            "emergence": [],
            "synergy": [],
            "transfer": [],
            "transferability": [],
            "noise": [],
            "optimization": [],
            "qml": []
        }
        self.load()

    def load(self):
        """
        Loads existing registry from JSON if it exists.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k in self.registry.keys():
                        if k in data:
                            self.registry[k] = data[k]
            except Exception as e:
                logger.error(f"Failed to load research registry: {e}")

    def register_run(self, category: str, metrics: Dict[str, Any]) -> None:
        """
        Registers an experimental run under a specific category.
        """
        if category not in self.registry:
            self.registry[category] = []
        self.registry[category].append(metrics)
        self.save()

    def save(self) -> None:
        """
        Saves the registry to research_registry.json.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save research registry: {e}")
            
    def get_runs(self, category: str) -> List[Dict[str, Any]]:
        return self.registry.get(category, [])
