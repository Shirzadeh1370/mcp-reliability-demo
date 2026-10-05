from __future__ import annotations

import logging
import os
import sys
from typing import Any

from fastmcp import FastMCP

from reliability_mcp.core import health_snapshot, summarize_usage, triage_incident

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("reliability_mcp")

mcp = FastMCP("Reliability Demo")


@mcp.tool
def health_check(service: str = "reliability-mcp") -> dict[str, Any]:
    """Return a small health payload for operational checks."""
    logger.info("health_check service=%s", service)
    return health_snapshot(service)


@mcp.tool
def incident_triage(
    error_message: str,
    service: str = "unknown",
    recent_change: str | None = None,
) -> dict[str, Any]:
    """Classify an error and suggest the first diagnostic checks."""
    result = triage_incident(error_message, service, recent_change)
    logger.info(
        "incident_triage service=%s category=%s severity=%s",
        service,
        result["category"],
        result["severity"],
    )
    return result


@mcp.tool
def usage_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize tool-call outcomes for a weekly usage export."""
    result = summarize_usage(events)
    logger.info(
        "usage_summary total_calls=%s failed_calls=%s",
        result["total_calls"],
        result["failed_calls"],
    )
    return result


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport == "http":
        mcp.run(transport="http", port=int(os.getenv("PORT", "8000")))
    else:
        mcp.run()
