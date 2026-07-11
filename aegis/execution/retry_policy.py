from __future__ import annotations


class RetryPolicy:
    def __init__(self, max_retries: int = 3):
        self.max_retries = int(max_retries)

    def should_retry(self, attempt: int, response) -> bool:
        return attempt < self.max_retries and getattr(response, "get", lambda *_: None)("status") == "retry"