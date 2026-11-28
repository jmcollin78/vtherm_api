# AGENTS.md - vtherm_api

Instructions for any AI coding agent (Claude Code, Codex, Copilot, others) working in this repository. They are meant to be sufficient on their own. Deeper knowledge lives in `.agents/` (versioned, shared memory). Answer in the language the user writes in; code, comments, commit messages and `.agents/` are in English.

## What this is

vtherm_api is the Python package, published on PyPI, that defines the contracts between Versatile Thermostat (VT) and its plugins: interfaces, registration, events, hooks and shared types. VT (separate repository) implements the VT side of each contract; plugins (algorithm, feature or UI plugins, separate repositories) implement the other side and depend only on this package.

## Start of a session: what to read

Always read `.agents/README.md` (index) and `.agents/context/principles.md` (binding rules). Then, by task:

| Task | Read |
| --- | --- |
| Any code change | `workflows/task-lifecycle.md`, `workflows/develop.md`, `context/architecture.md`, `context/pitfalls.md` |
| Adding or changing a contract | `context/contracts.md`, `context/decisions.md` |
| Bug analysis | `context/pitfalls.md`, then the `vtherm-api-debugger` profile |
| Tests | `workflows/testing.md` |
| Release | `workflows/release.md` |
| Past choices (do not re-propose rejected ideas) | `context/decisions.md` |
| Which sub-agent to use | `workflows/delegation.md` (`vtherm-api-*` profiles) |
| Finishing any task | `workflows/memory-maintenance.md` |

Load only what the task needs: grep and partial reads.

## Hard rules

1. **No hallucination.** Every claim rests on code, docs, observed data or a demonstrable argument; mark the rest "unverified". When a decision is not certain, stop and ask.
2. **Plan first.** A non-trivial task starts with a written plan (`.agents/templates/plan.md`) in the local task folder, validated by the user before any code. Trivial tasks get a three-line plan in the conversation. See `workflows/task-lifecycle.md`.
3. **Contracts first, backward compatible.** A cross-repository feature changes this package first; every change keeps existing plugins and VT releases working (new optional members, defaults), bumps the version, and is followed by VT, then by the plugins.
4. **Quality, no shortcuts.** Simple, readable code; English comments and docstrings that explain why. Fix root causes: no swallowed errors, special-case flags, test-only branches, duplicated logic. Contracts run inside the Home Assistant event loop: no I/O, no blocking calls, no heavy work in the package. Details: `workflows/develop.md`.
5. **Stay in scope.** Change only what the task needs; do not fix other things unasked. Re-read every diff you produced. Always `git --no-pager`.
6. **No commits.** Never commit, push, tag or publish unless the user expressly asks. After a change, give a brief English commit message (no links, no file paths).
7. **Tests.** pytest, targeted files first (`workflows/testing.md`). Long runs go in the background: wait for the completion notification, never poll a running job.
8. **Docs.** Documentation describes the current state only, as if never published (no "new/now/fixed/changed" wording). After a user-visible change update the README and the docs.
9. **No private context in the repository.** Code, comments, docs, tests and `.agents/` never mention plans, phases, review identifiers, personal names, credentials, URLs of private systems, real entity ids or machine-specific paths.
10. **Cost discipline.** Cheapest adequate model per sub-task, tight briefs, short reports, a fresh sub-agent per task (`workflows/delegation.md`).

## Commands

```bash
python -m pip install -r requirements-dev.txt && python -m pip install -e .   # dev environment (re-run after a version bump)
python -m pytest tests/test_<module>.py     # targeted tests first
python -m pytest                            # full suite (background task, never polled)
python -m build && python -m twine check dist/*   # packaging check (see workflows/release.md)
python3 .agents/scripts/check_memory.py   # memory consistency check
git --no-pager status --short ; git --no-pager diff --stat
```

## Repository map (short)

- `src/vtherm_api/`: the package. `interfaces.py` (base protocols), `vtherm_api.py` (`VThermAPI` singleton, registries, inhibition facade), `plugin_climate.py` (event relay), `command_receipt.py`, `underlying_hooks.py`, `valve_write.py`, `setpoint_modifier.py`, `calibration_modifier.py` (optional contracts), `ui_plugin.py`, `log_collector.py`, `const.py`; `__init__.py` holds the exports and `__version__`.
- `tests/`: one file per contract; `test_backward_compatibility.py` freezes the public surface.
- `documentation/en/`: API reference, events, guides (the contract rules mirror the module docstrings); `README.md`.
- `publish.md` (French) and the `Tests` and `Release` workflows in `.github/workflows/`: packaging and PyPI publication.
- `pyproject.toml` (dynamic version, no runtime dependency), `requirements-dev.txt` (pinned Home Assistant for tests).
- `.agents/`: shared memory.
- `.github/agents/`: the generated `vtherm-api-*` profiles and the maintainers' own Copilot profiles.

Full map: `.agents/context/architecture.md`.

## Two memory tiers

- **Long-term, versioned**: `.agents/context/` - the current truth about the project, shared with every developer. A fact enters it only if it passes the admission test of `workflows/memory-maintenance.md`.
- **Short-term, local, never versioned**: `.agents/local/tasks/<task-slug>/` with `plan.md`, `notes.md`, `handoff.md`. Work in progress, findings, dead ends, resumption state. Deleted when the task closes, after promoting the few durable facts.

Every task ends with the checklist of `workflows/memory-maintenance.md` and a line "memory: updated X" or "memory: nothing to update because ...".
