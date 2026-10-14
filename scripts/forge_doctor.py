#!/usr/bin/env python3
"""Non-mutating Hermes Forge foundation diagnostics (stdlib only)."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def classify_error(message: str) -> dict[str, object]:
    """Classify an error without returning any untrusted message contents."""
    m = message.lower()
    if ("403" in m or "forbidden" in m) and (
        "ip" in m or "network" in m or "authoriz" in m
    ):
        return {"code": "unauthorized_network", "retryable": False}
    if "401" in m or "invalid api key" in m or "invalid credential" in m:
        return {"code": "invalid_credentials", "retryable": False}
    if "403" in m or "forbidden" in m:
        return {"code": "forbidden", "retryable": False}
    if "429" in m or "rate limit" in m:
        return {"code": "rate_limited", "retryable": True}
    if any(s in m for s in ("name resolution", "dns", "getaddrinfo", "nxdomain")):
        return {"code": "dns_failure", "retryable": True}
    if "timeout" in m or "timed out" in m:
        return {"code": "timeout", "retryable": True}
    if any(s in m for s in ("502", "503", "504", "server unavailable")):
        return {"code": "upstream_unavailable", "retryable": True}
    return {"code": "unknown", "retryable": False}


def inspect(home: Path, min_free_mb: int = 512) -> dict[str, object]:
    if min_free_mb < 0:
        raise ValueError("Minimum free space must be nonnegative")
    # Inspect an existing parent if the target profile doesn't exist yet.
    probe = home.expanduser().resolve()
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    if not probe.is_dir():
        raise ValueError("Profile path has no usable parent directory")
    disk = shutil.disk_usage(probe)
    free_mb = disk.free // (1024 * 1024)
    status = "critical" if free_mb < min_free_mb else "healthy"
    return {
        "service": "hermes-forge",
        "version": "0.1.0",
        "status": status,
        "runtime": {
            "hermes_detected": shutil.which("hermes") is not None,
            "profile_exists": home.expanduser().is_dir(),
            "gateway": "not_checked",
        },
        "system": {"disk_status": status, "disk_free_mb": free_mb},
        "recovery": {"automatic_restart": False},
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Read-only Hermes Forge diagnostics")
    p.add_argument("--home", type=Path, default=Path(os.environ.get("HERMES_HOME", "~/.hermes")))
    p.add_argument("--min-free-mb", type=int, default=512)
    p.add_argument("--classify-error", metavar="TEXT")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    try:
        report = inspect(args.home, args.min_free_mb)
    except (ValueError, OSError) as exc:
        p.error(str(exc))
    if args.classify_error is not None:
        report["provider_error"] = classify_error(args.classify_error)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Hermes Forge v{report['version']} — {report['status']}")
        print(f"Hermes on PATH: {report['runtime']['hermes_detected']}")
        print(f"Profile exists: {report['runtime']['profile_exists']}")
        print(f"Free disk: {report['system']['disk_free_mb']} MiB")
        if "provider_error" in report:
            print(f"Provider issue: {report['provider_error']['code']}")
    return 2 if report["status"] == "critical" else 0


if __name__ == "__main__":
    sys.exit(main())
