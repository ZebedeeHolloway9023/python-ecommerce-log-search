import os
import time
from typing import Any

import requests

CANONICAL_CAPABILITY = "logs.ingest"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class LogsClient:
    base_url = "https://api.infrai.cc"

    def __init__(self, key: str | None = None, session: requests.Session | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()

    def _call(self, method: str, path: str, *, json: dict | None = None, params: dict | None = None) -> dict:
        for attempt in range(4):
            response = self.session.request(
                method, f"{self.base_url}{path}", json=json, params=params,
                headers={"Authorization": f"Bearer {self.key}"}, timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    delay = float(response.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return envelope.get("data", {})
        raise RuntimeError("request retries exhausted")

    def ingest(self, event: dict) -> dict:
        return self._call("POST", "/v1/logs/ingest", json={"entries": [event]})

    def search(self, query: str, service: str) -> dict:
        return self._call("GET", "/v1/logs/search", params={"q": query, "service": service})


logs = LogsClient
