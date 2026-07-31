"""Run pyright and report each static type error as a separate test case.

Run with:
    pytest tests/test_static.py

When the codebase is clean (no pyright errors), this file generates a
single passing test (`test_pyright_clean`). When pyright finds N errors,
it generates one baseline failure plus N parametrized failures — one per
error — each named after its file/line/rule.
"""

import json
from typing import Any

import pyright
import pytest


def _collect_pyright_diagnostics() -> list[dict[str, Any]]:
    """Run pyright with JSON output and return the list of error diagnostics."""
    response = pyright.cli.run("--outputjson", capture_output=True)
    if response.returncode not in (0, 1):
        stderr = response.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"pyright exited unexpectedly with code {response.returncode}: {stderr}")
    stdout = response.stdout
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8")
    payload = json.loads(stdout)
    diagnostics = payload.get("generalDiagnostics", [])
    return [d for d in diagnostics if d.get("severity") == "error"]


def _format_diag(diag: dict[str, Any]) -> str:
    """One-line diagnostic message: `<file>:<line>:<col> [<rule>] <msg>`."""
    if not isinstance(diag, dict) or "file" not in diag:
        return "clean"
    file = diag["file"].rsplit("/", 1)[-1]
    line = diag.get("range", {}).get("start", {}).get("line", 0) + 1
    col = diag.get("range", {}).get("start", {}).get("character", 0) + 1
    rule = diag.get("rule") or "unknown"
    return f"  {file}:{line}:{col} [{rule}] {diag.get('message', '')}"


def _case_id(diag: dict[str, Any]) -> str:
    """Stable pytest test id for one diagnostic."""
    return _format_diag(diag).strip()


# Collect once at module load — one pyright run, one list of errors.
_DIAGNOSTICS = _collect_pyright_diagnostics()


_DIAG_PARAM = _DIAGNOSTICS if _DIAGNOSTICS else [{}]


def test_pyright_clean() -> None:
    """Baseline: pyright reports zero static type errors in the codebase."""
    if _DIAGNOSTICS:
        pytest.fail(
            f"pyright found {len(_DIAGNOSTICS)} static type error(s):\n"
            + "\n".join(_format_diag(d) for d in _DIAGNOSTICS)
        )


@pytest.mark.skipif(not _DIAGNOSTICS, reason="no pyright errors to report")
@pytest.mark.parametrize("diag", _DIAG_PARAM, ids=_case_id)
def test_pyright_diagnostic(diag: dict[str, Any]) -> None:
    """Each pyright error becomes its own failing test (for CI dashboards)."""
    pytest.fail(_format_diag(diag))

