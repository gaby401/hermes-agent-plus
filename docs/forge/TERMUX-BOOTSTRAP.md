# Termux bootstrap status

## Confirmed issue

The development `setup-hermes.sh` identifies Android/Termux as `linux-arm64`, selects a GNU/Linux uv binary, and attempts to execute it. Android Bionic cannot execute that binary, producing `cannot execute: required file not found`.

The PM lock contains a `linux-arm64-bionic` row for uv and Python, but these are Termux `.deb` packages. The existing bootstrap expects a tar or zip and calls `uv python install --no-bin --no-registry` for standalone Python. Switching `target` alone will not work.

## Current change

The bootstrap now detects Termux before touching its tool store and prints an actionable error. This is a **guard**, not a complete installation solution. It does not change or delete the production Hermes installation.

## Follow-up engineering work

1. Introduce a shared platform-target detector for setup shell and Python PM.
2. Build a verified .deb extraction path for pinned Termux artifacts, handling paths, permissions and nonexecutability.
3. Ensure bootstrap Python discovery uses the pinned Termux Python or an explicitly supported compatible interpreter.
4. Make sure `HERMES_RUNTIME_DIR` isolates tool artifacts and `HERMES_HOME` isolates session/config profiles.
5. Validate dependencies and interpreter ABI on a real Termux arm64 host before advertising support.
6. Run upstream checks and host-specific end-to-end tests.

## Safe current command

```sh
cd ~/hermes-forge
python scripts/forge_doctor.py --json
```

Never overwrite `~/.hermes/hermes-agent`, remove `~/.hermes/tools`, or launch a second Telegram gateway with the same bot token during development.
