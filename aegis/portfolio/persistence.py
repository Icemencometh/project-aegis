from __future__ import annotations


class PortfolioStore:
    def __init__(self):
        self._snapshot = None

    def save(self, snapshot):
        self._snapshot = dict(snapshot or {})
        return self._snapshot

    def load(self):
        return dict(self._snapshot or {})
