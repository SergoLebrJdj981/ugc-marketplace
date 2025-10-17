"""Lightweight runtime metrics collection."""

from __future__ import annotations

import threading
import time

_start_time = time.time()
_request_count = 0
_error_count = 0
_lock = threading.Lock()


def record_request() -> None:
    global _request_count
    with _lock:
        _request_count += 1


def record_error() -> None:
    global _error_count
    with _lock:
        _error_count += 1


def snapshot() -> dict[str, float | int]:
    now = time.time()
    uptime_seconds = max(now - _start_time, 0.0)
    minutes = max(uptime_seconds / 60.0, 1.0)
    with _lock:
        requests = _request_count
        errors = _error_count
    return {
        "uptime": uptime_seconds,
        "requests_total": requests,
        "requests_per_min": requests / minutes,
        "errors": errors,
    }


def reset_metrics() -> None:
    global _request_count, _error_count
    with _lock:
        _request_count = 0
        _error_count = 0
    global _start_time
    _start_time = time.time()
