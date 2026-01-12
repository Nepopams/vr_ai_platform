"""HTTP server for local agent runner."""

from __future__ import annotations

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from agent_runner import config
from agent_runner.envelope import (
    A2A_VERSION,
    SUPPORTED_AGENT_ID,
    SUPPORTED_INTENT,
    build_response,
    parse_request,
    unsupported_response,
)
from agent_runner.shopping_agent import extract_shopping_items


class AgentRunnerHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/a2a/v1/invoke":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid_json"})
            return

        try:
            request = parse_request(payload)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return

        if request.agent_id != SUPPORTED_AGENT_ID or request.intent != SUPPORTED_INTENT:
            response = unsupported_response(request)
            self._send_json(200, response)
            return

        started = time.perf_counter()
        ok, result = extract_shopping_items(request.input_text, request.input_context)
        latency_ms = int((time.perf_counter() - started) * 1000)
        meta = result.get("meta", {})
        meta["latency_ms"] = latency_ms
        response = build_response(
            request=request,
            ok=ok,
            output=result.get("output"),
            meta=meta,
            error=result.get("error"),
        )
        self._send_json(200, response)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run() -> None:
    server = HTTPServer((config.get_host(), config.get_port()), AgentRunnerHandler)
    server.serve_forever()


if __name__ == "__main__":
    run()
