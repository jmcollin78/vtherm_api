# Principles (binding)

Rules stated by the maintainers. An agent that finds a task conflicting with one of them stops and asks. The user may waive a rule for one task; it applies again once that task is done.

## Architecture

- **Contracts first, backward compatible.** A cross-repository feature changes this package first; every change keeps existing plugins and VT releases working (new optional members, defaults), bumps the version, and is followed by VT, then by the plugins.
- **Optional capabilities are separate protocols.** A plugin-implemented protocol never gains a required member. A new capability is a new `@runtime_checkable` protocol next to the unchanged base one; the core detects it with `hasattr` or `isinstance`. Only core-implemented protocols (`InterfaceThermostatRuntime`, `InterfaceCycleScheduler`) can grow, and VT implements the member before raising its minimum requirement.
- **The package is passive.** It holds types, registries and relays; policy lives in VT or in plugins (the UI plugin registry does not interpret its entries, the inhibition facade only delegates). Nothing here decides thermostat behavior.
- **One public surface.** Every public name is exported from `src/vtherm_api/__init__.py` and frozen by `tests/test_backward_compatibility.py` and `tests/test_package.py`; a contract change updates code, docstring, `documentation/en/api-reference.md` and tests together.
- **One mechanism per job.** Reuse the existing module or helper instead of a parallel path doing the same thing.

## Code quality

- Simple, readable code that a non-specialist can follow. Clear names, small functions, early returns.
- English comments and docstrings on public functions, classes and components; they explain intent and constraints, not history.
- Elegant solutions only: fix the root cause; no shortcut taken because it is easier (swallowed errors, special-case flags, test-only branches, copy-paste, sleeps to dodge races).
- Contracts run inside the Home Assistant event loop: no I/O, no blocking calls, no heavy work in the package.
- Types on new code; named constants, no magic numbers.

## Process

- Plan before coding; the user validates the plan of a non-trivial task (`workflows/task-lifecycle.md`).
- Proceed step by step; validate each step before the next.
- Change only what the task requires; re-read the diff after each edit.
- No commit, push, tag or publish without an express request.
- Evidence before claims: say what was verified and how; mark the rest "unverified".
- Token economy: grep and partial reads, the cheapest adequate sub-agent, concise answers.

## Documentation

- Docs describe the current state only, as if never published; only release notes and the changelog list changes.
- A user-visible change updates the README and the docs in the same change set.

## Repository hygiene

- Nothing private or install-specific in versioned files: no plan or review references, people names, credentials, private URLs, real entity ids, absolute or machine paths.
- Commit messages are brief, informative, in English, without links or file paths.
