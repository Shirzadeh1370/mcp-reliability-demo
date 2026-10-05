# MCP Reliability Demo

A compact Python + FastMCP project that demonstrates reliability-focused engineering for AI/MCP services: deterministic incident triage, health checks, usage summaries, logging, and regression tests.

## Why this project

AI services are useful only when failures can be understood and reproduced. This demo keeps the MCP transport layer thin and moves diagnostic behavior into deterministic Python functions that can be tested without starting the server.

## MCP tools

- `health_check` — returns a small deterministic health payload.
- `incident_triage` — classifies common authentication, network, schema, resource, and dependency failures and returns practical first checks.
- `usage_summary` — summarizes tool-call outcomes for a lightweight weekly usage export.

## Stack

- Python 3.11+
- FastMCP 4
- pytest
- GitHub Actions

## Project structure

```text
mcp-reliability-demo/
├── .github/workflows/tests.yml
├── examples/usage_events.json
├── src/reliability_mcp/
│   ├── __init__.py
│   ├── core.py
│   └── server.py
├── tests/test_core.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Run locally

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
fastmcp run src/reliability_mcp/server.py:mcp
```

The current regression suite contains **7 tests** covering health output, authentication failures, timeout/network failures, high-severity incidents, unknown failures, usage summaries, and empty usage input.

## HTTP transport

```powershell
$env:MCP_TRANSPORT="http"
$env:PORT="8000"
python -m reliability_mcp.server
```

A compatible MCP client can then connect to:

```text
http://localhost:8000/mcp
```

## Example incident

Input:

```text
service = "billing-api"
error_message = "403 Forbidden: OAuth token expired"
```

Example result:

```json
{
  "service": "billing-api",
  "category": "authentication",
  "severity": "medium",
  "recent_change_provided": false,
  "recommended_checks": [
    "Verify credentials or token freshness.",
    "Check scopes/permissions and recent auth configuration changes.",
    "Reproduce with the smallest authenticated request."
  ]
}
```

## Reliability design choices

- **Deterministic core logic:** failures are easier to reproduce and convert into regression tests.
- **Transport separation:** MCP wrappers are separate from diagnostic functions.
- **Fail-visible behavior:** unknown conditions stay explicit instead of silently becoming a guessed category.
- **Structured outputs:** tool results are straightforward for clients and downstream automation to consume.
- **No user-content storage:** the usage summary operates on supplied event metadata only.

## What was challenging

The most important design problem was keeping transport concerns separate from diagnostic logic. That makes a failure reproducible in a unit test instead of requiring an MCP client and live server every time. I also kept the triage rules transparent so incorrect classifications can be fixed with a small regression test.

## Next improvements

- Structured JSON logging and request correlation IDs
- Retry/backoff metrics for dependency failures
- Containerized deployment for AWS ECS/Fargate
- DynamoDB/S3-backed usage export
- Authentication and OAuth integration examples

---

Built as a focused engineering sample for learning and demonstrating Python, MCP, debugging, testing, and reliability practices.
