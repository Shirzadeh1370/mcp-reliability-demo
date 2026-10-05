from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


def health_snapshot(service: str = "reliability-mcp") -> dict[str, Any]:
    """Return a deterministic health payload suitable for a lightweight check."""
    return {
        "service": service,
        "status": "ok",
        "version": "0.1.0",
    }


def triage_incident(
    error_message: str,
    service: str = "unknown",
    recent_change: str | None = None,
) -> dict[str, Any]:
    """Classify a failure and return practical first checks.

    The function intentionally uses transparent rules so its behavior is easy to
    test and debug. It is designed as the deterministic core behind an MCP tool.
    """
    text_value = f"{error_message} {recent_change or ''}".lower()

    categories: list[tuple[str, tuple[str, ...], list[str]]] = [
        (
            "authentication",
            ("401", "403", "unauthorized", "forbidden", "token", "credential", "oauth", "auth"),
            [
                "Verify credentials or token freshness.",
                "Check scopes/permissions and recent auth configuration changes.",
                "Reproduce with the smallest authenticated request.",
            ],
        ),
        (
            "timeout_or_network",
            ("timeout", "timed out", "connection refused", "connection reset", "dns", "socket", "network"),
            [
                "Check endpoint reachability, DNS, and recent network changes.",
                "Compare client timeout with upstream latency.",
                "Retry once with backoff and capture the exact failure boundary.",
            ],
        ),
        (
            "data_or_schema",
            ("schema", "validation", "json", "decode", "parse", "missing field", "keyerror", "typeerror"),
            [
                "Capture the failing input without secrets.",
                "Compare input shape with the expected schema.",
                "Add or run a regression test for the failing payload.",
            ],
        ),
        (
            "capacity_or_resource",
            ("out of memory", "oom", "memory", "disk full", "no space", "throttle", "rate limit", "429"),
            [
                "Check resource metrics and service quotas.",
                "Identify whether load or a recent deployment changed usage.",
                "Reduce concurrency or apply bounded backoff if appropriate.",
            ],
        ),
        (
            "dependency",
            ("upstream", "dependency", "502", "503", "504", "service unavailable", "bad gateway"),
            [
                "Check upstream status and dependency health.",
                "Confirm whether the failure is isolated to one dependency.",
                "Use a fail-closed or degraded path instead of silently continuing.",
            ],
        ),
    ]

    category = "unknown"
    checks = [
        "Reproduce the issue with the smallest input.",
        "Check logs around the first failure, not only the final exception.",
        "Compare the last known-good version or configuration.",
    ]

    for name, keywords, recommendations in categories:
        if any(keyword in text_value for keyword in keywords):
            category = name
            checks = recommendations
            break

    severe_terms = ("data loss", "security", "breach", "crash", "down", "corrupt", "unavailable")
    severity = "high" if any(term in text_value for term in severe_terms) else "medium"
    if category == "unknown" and severity != "high":
        severity = "low"

    return {
        "service": service,
        "category": category,
        "severity": severity,
        "recent_change_provided": bool(recent_change),
        "recommended_checks": checks,
    }


def summarize_usage(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize tool usage events without storing user content."""
    materialized = list(events)
    total = len(materialized)
    if total == 0:
        return {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "error_rate": 0.0,
            "calls_by_tool": {},
        }

    by_tool: Counter[str] = Counter()
    success = 0
    for event in materialized:
        by_tool[str(event.get("tool", "unknown"))] += 1
        status = str(event.get("status", "unknown")).lower()
        if status in {"ok", "success", "succeeded"}:
            success += 1

    failed = total - success
    return {
        "total_calls": total,
        "successful_calls": success,
        "failed_calls": failed,
        "error_rate": round(failed / total, 4),
        "calls_by_tool": dict(sorted(by_tool.items())),
    }
