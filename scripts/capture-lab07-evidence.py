#!/usr/bin/env python3
"""Capture repeatable HTTP evidence from the running Laboratory Work 7 app."""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://localhost:8080"


def call(method, path, body=None, headers=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request_headers = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        BASE + path, data=data, headers=request_headers, method=method
    )
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as error:
        response = error
    raw = response.read().decode("utf-8")
    content_type = response.headers.get("Content-Type", "")
    parsed = json.loads(raw) if raw and "json" in content_type else raw
    return {
        "request": f"{method} {path}",
        "status": response.status,
        "contentType": content_type,
        "location": response.headers.get("Location"),
        "body": parsed,
    }


observations = []
observations.append(call("GET", "/api/books"))
observations.append(call("GET", "/api/books/1"))
observations.append(call("GET", "/api/books/999"))

created = call(
    "POST",
    "/api/books",
    {
        "title": f"HTTP Evidence {time.time_ns()}",
        "author": "Evidence Author",
        "year": 2026,
        "genre": "SCIENCE",
    },
)
observations.append(created)
location = created["location"]
if not location:
    raise RuntimeError("POST did not return Location")
observations.append(call("GET", location))
observations.append(call("DELETE", location))
observations.append(call("DELETE", location))

observations.append(
    call(
        "POST",
        "/api/books",
        {"title": "", "author": "Valid Author", "year": 2026, "genre": "SCIENCE"},
    )
)
observations.append(
    call(
        "POST",
        "/api/books",
        {
            "title": "Effective Java",
            "author": "Joshua Bloch",
            "year": 2018,
            "genre": "TECHNOLOGY",
        },
    )
)
observations.append(call("GET", "/api/books/search?q=Java"))
observations.append(call("GET", "/api/books/search?q=a"))

openapi = call("GET", "/v3/api-docs")
schema = openapi["body"]["components"]["schemas"]["BookRequest"]
summary = {
    "capturedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "baseUrl": BASE,
    "observations": observations,
    "openapi": {
        "version": openapi["body"]["openapi"],
        "bookPaths": sorted(path for path in openapi["body"]["paths"] if path.startswith("/api/books")),
        "bookMethods": {
            path: sorted(openapi["body"]["paths"][path])
            for path in openapi["body"]["paths"]
            if path.startswith("/api/books")
        },
        "bookRequest": schema,
    },
}

output = ROOT / "docs" / "lab07-observations.json"
output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(output)
