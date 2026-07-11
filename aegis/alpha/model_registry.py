from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ModelRegistry:
    models: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def register(self, name: str, metadata: Dict[str, Any] | None = None):
        self.models[str(name)] = dict(metadata or {})
        return str(name)

    def get(self, name: str) -> Dict[str, Any]:
        return dict(self.models.get(str(name), {}))

    def list_models(self):
        return sorted(self.models)