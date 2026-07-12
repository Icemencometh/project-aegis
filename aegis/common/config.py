"""Config loading for Aegis.

Per Aegis_Coding_Standards.txt ("All runtime behavior controlled via config
files and environment variables. No hard-coded magic numbers or secrets."),
every Aegis engine should be constructed with a config dict loaded from
aegis/config/*.yaml rather than literal values baked into code.

This module is the single place that turns those YAML files into plain
dicts. It has no side effects beyond reading files from disk and never
mutates the files it reads.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import yaml

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
CONFIG_NAMES = ("risk", "portfolio", "execution", "scoring")


def load_yaml(path: str) -> Dict[str, Any]:
    """Load a YAML file into a plain dict. Missing files return {} (safe default)."""
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return dict(data or {})


def load_config(name: str, config_dir: Optional[str] = None) -> Dict[str, Any]:
    """Load a single named Aegis config file (e.g. "risk" -> risk.yaml)."""
    directory = config_dir or CONFIG_DIR
    return load_yaml(os.path.join(directory, f"{name}.yaml"))


def load_all_configs(config_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Load every known Aegis config file, keyed by name.

    Unwraps the single top-level key each file uses today (e.g. risk.yaml's
    top-level `limits:` block, portfolio.yaml's `portfolio:` block) so callers
    get a flat dict ready to pass into a constructor, while still tolerating
    files that don't use a wrapper key.
    """
    directory = config_dir or CONFIG_DIR
    wrapper_keys = {
        "risk": None,  # risk.yaml keeps its own "limits" nesting intentionally
        "portfolio": "portfolio",
        "execution": "execution",
        "scoring": None,
    }
    configs: Dict[str, Dict[str, Any]] = {}
    for name in CONFIG_NAMES:
        raw = load_config(name, directory)
        wrapper = wrapper_keys.get(name)
        if wrapper and wrapper in raw:
            configs[name] = dict(raw[wrapper])
        else:
            configs[name] = raw
    return configs
