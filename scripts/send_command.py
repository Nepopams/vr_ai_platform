#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.request


def load_payload(path: str) -> bytes:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Отправка CommandDTO в AI Platform")
    parser.add_argument(
        "--file",
        default="docs/integration/examples/create_task_start_job.json",
        help="Путь к JSON с CommandDTO",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/decide",
        help="URL Decision API",
    )
    args = parser.parse_args()

    try:
        data = load_payload(args.file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Ошибка чтения файла: {exc}", file=sys.stderr)
        return 1

    request = urllib.request.Request(
        args.url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        print(f"Ошибка запроса: {exc}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        print(f"Невалидный JSON в ответе: {exc}", file=sys.stderr)
        print(body)
        return 1

    action = payload.get("action")
    trace_id = payload.get("trace_id")
    job_type = None
    payload_body = payload.get("payload")
    if isinstance(payload_body, dict):
        job_type = payload_body.get("job_type")

    print(f"action: {action}")
    print(f"job_type: {job_type}")
    print(f"trace_id: {trace_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
