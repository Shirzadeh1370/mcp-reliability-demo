from reliability_mcp.core import health_snapshot, summarize_usage, triage_incident


def test_health_snapshot_is_ok():
    result = health_snapshot("demo")
    assert result == {"service": "demo", "status": "ok", "version": "0.1.0"}


def test_triage_auth_failure():
    result = triage_incident("403 Forbidden: OAuth token expired", "api")
    assert result["category"] == "authentication"
    assert result["severity"] == "medium"
    assert len(result["recommended_checks"]) >= 3


def test_triage_timeout_failure():
    result = triage_incident("upstream request timed out", "mcp-gateway")
    assert result["category"] == "timeout_or_network"


def test_triage_high_severity():
    result = triage_incident("service unavailable after crash", "worker")
    assert result["severity"] == "high"


def test_triage_unknown_is_low():
    result = triage_incident("unexpected behavior", "worker")
    assert result["category"] == "unknown"
    assert result["severity"] == "low"


def test_usage_summary():
    result = summarize_usage(
        [
            {"tool": "incident_triage", "status": "ok"},
            {"tool": "incident_triage", "status": "error"},
            {"tool": "health_check", "status": "success"},
        ]
    )
    assert result["total_calls"] == 3
    assert result["successful_calls"] == 2
    assert result["failed_calls"] == 1
    assert result["error_rate"] == 0.3333
    assert result["calls_by_tool"] == {"health_check": 1, "incident_triage": 2}


def test_empty_usage_summary():
    result = summarize_usage([])
    assert result["total_calls"] == 0
    assert result["error_rate"] == 0.0
