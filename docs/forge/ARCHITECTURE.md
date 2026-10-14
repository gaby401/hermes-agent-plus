# Hermes Forge — Architecture v0.1

Hermes Forge is a modular AI operating system built as an extension of Nous Research's Hermes Agent. Three product surfaces share a single agent runtime:

- **Personal:** persistent assistant, messaging, scheduled jobs and memory.
- **Developer:** isolated worktrees, code editing, verification and human-reviewed changes.
- **Platform:** connected machines, automation, diagnostics and control UI.

## Principles

1. Preserve Hermes agent loop, gateway, prompt caching and upstream interfaces.
2. Extend existing functionality before adding a Forge-specific implementation.
3. Put optional capabilities behind plugins, CLI commands or service-gated tools.
4. Separate the control plane (intent, authorization, coordination) from workers (execution).
5. Require explicit approval for destructive, financial, remote-execution and credential-related actions.
6. Store behavioral settings in config.yaml and secrets in the existing secret storage; never commit credentials.
7. Do not log sensitive prompts, tokens or environment values.
8. Use profile-aware Hermes paths and isolated test/development profiles.
9. Every recovery action is bounded, logged, and independently verified.
10. Stay mergeable with upstream main; favor additive changes.

## Proposed components

| Component | Responsibility | Milestone |
| --- | --- | --- |
| Forge Doctor | Non-mutating local health and environment diagnostics | M1 |
| Forge Supervisor | Bounded, approved gateway recovery | M1 follow-up |
| Forge API | Authenticated localhost diagnostics and controls | M1 follow-up |
| Forge Router | Provider capability and failure classification | M2 |
| Forge Tasks | Durable coordinated task execution | M3 |
| Forge Bridge | Authenticated Windows/Termux worker coordination | M3 |
| Forge Studio | Isolated coding agent workflow | M4 |
| Forge UI | Desktop/mobile responsive control center | M4 |
| Forge Memory | Search and governance atop Hermes memory | M5 |

Existing Hermes functionality is canonical; modules above are planned and should not be duplicated when upstream already supplies equivalent behavior.

## Runtime boundaries

**Diagnostics:** read only, local first. No API keys or full configuration contents in output.

**Actions:** authenticated, allowlisted operations only. A failure such as HTTP 403 due to an unauthorized network must not trigger an infinite restart loop.

**Devices:** future remote workers connect using an authenticated, encrypted channel; never expose a raw shell over an unauthenticated WebSocket.

**Development:** agent-generated code lives on a separate branch/worktree, tests run before review, and production configuration is never used by tests.

## Upstream reference

Follow root `AGENTS.md`, topic-specific `AGENTS.md`, `CONTRIBUTING.md`, and `scripts/run_tests.sh` when changing existing Hermes behavior.
