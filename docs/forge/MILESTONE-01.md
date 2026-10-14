# M1 — Forge Foundation

## Goal

Deliver non-destructive local diagnostics in the fork, then add a bounded recovery mechanism behind explicit authorization. Initial code must not alter normal Hermes startup.

## First deliverable: Forge Doctor

Entry point: `python scripts/forge_doctor.py`.

- Output readable diagnostics by default, or machine-readable JSON with `--json`.
- Discover whether a Hermes executable is present on PATH.
- Inspect an explicitly chosen directory with `--home PATH`, otherwise use the Hermes profile path without assuming permission to modify it.
- Check disk space using the filesystem hosting the chosen profile path.
- Classify known provider error messages supplied directly via `--classify-error TEXT`; never echo the raw error or possible keys.
- Return exit code 0 for healthy/warning, 2 for critical conditions, and 1 for invalid input.
- Run without importing Hermes modules or installing new dependencies.

## Acceptance tests

- No Hermes installation: doctor returns a useful report, not a traceback.
- Low disk threshold: critical warning without automatic cleanup.
- Provider error 403/unauthorized network: categorized as `unauthorized_network` and marked non-retryable.
- DNS, rate-limit, timeout and transient server errors are distinguishable.
- Error report does not echo supplied credentials, provider URLs or raw errors.
- Read-only invocation leaves the profile unchanged.
- Check works on Windows and Termux.

## Next PR scope (not part of the initial diagnostic script)

- Integrate Hermes profile-aware runtime and command discovery after auditing the relevant module contracts.
- Introduce tests under the existing Hermes test runner and isolated `HERMES_HOME`.
- Implement supervisor restart only with user confirmation, cooldown, idempotency and post-restart check.
- Add localhost-only health API after explicit authentication and safety review.
- Verify behavior on the actual supported hosts.

## Verification

Run `python scripts/forge_doctor.py --json` and `python -m unittest discover -s tests/forge -v` for the initial standalone component. For broader Hermes changes use `scripts/run_tests.sh` and `python scripts/check` as required by the upstream project.
