from __future__ import annotations


class ExecutionMetrics:
    def __init__(self):
        self.submissions = 0
        self.fills = 0

    def record_submission(self):
        self.submissions += 1

    def record_fill(self):
        self.fills += 1

    def snapshot(self, *args, **kwargs):
        return {"submissions": self.submissions, "fills": self.fills}