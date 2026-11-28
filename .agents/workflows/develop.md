# Develop

Rules for writing code in this package. Principles: `context/principles.md`; contract procedure: `context/contracts.md`.

## Where code goes

| Need | Place |
| --- | --- |
| A new optional capability of a manager or scheduler | A new module `src/vtherm_api/<capability>.py` (protocol, payloads, rules in the module docstring), exported from `src/vtherm_api/__init__.py`. Not a new member of an existing plugin-implemented protocol. |
| A member of the runtime or scheduler seen by plugins | `src/vtherm_api/interfaces.py`; only with VT ready to implement it. |
| A registry or a facade operation | `src/vtherm_api/vtherm_api.py::VThermAPI`, delegating the substance to a small module (see `src/vtherm_api/ui_plugin.py`). |
| A constant shared with VT | `src/vtherm_api/const.py`; export it from the package root only when plugins need it. |
| A helper only a test needs | The test file, not the package (`VThermAPI._set_now` and `NowClass.get_now` are the test clock hooks; do not add more). |

## How code is written

- Python 3.13 compatible (`requires-python`), even though CI runs 3.14. Type hints on new code; `from __future__ import annotations` as in the sibling modules.
- Contracts are `@runtime_checkable` `Protocol` classes with a one-line docstring per member; payloads are `@dataclass(frozen=True, slots=True)`, fields documented by an attribute docstring, new fields last with a default. New enumerations are `StrEnum` (`EventType` is a plain `Enum`: compare with `.value`).
- The module docstring of a contract states, as a bullet list: who calls, when, sync or async, ordering, timeout, error handling, what is not covered. Mirror it in `documentation/en/api-reference.md` in the same change.
- English docstrings and comments, explaining why. Named constants, no magic numbers (`UNDERLYING_HOOK_TIMEOUT_SEC` style, with a docstring on the constant).
- Validation raises `ValueError` / `TypeError` / `LookupError` with a message naming the faulty field or id; error texts shared with the docs are module constants (`ERROR_*` in `src/vtherm_api/ui_plugin.py`).
- Optional behaviour of a possibly older core is read with `getattr(obj, name, default)` and documented (`VThermAPI.is_inhibition_started`).
- Logging: `_LOGGER = get_vtherm_logger(__name__)` from `src/vtherm_api/log_collector.py`, messages shaped `"%s - text"` with the thermostat or API object first, so the export filters can attribute them. Lazy `%s` arguments, no f-strings in log calls.
- Pylint disables are inline with a reason, as in the existing code. Line length 180. Keep the import graph acyclic (`context/architecture.md`).

## Performance and event loop

- The package runs inside the Home Assistant event loop: no blocking call, no file or network I/O, no heavy computation in a contract method. The only file I/O is the log export and the log download view; the export runs in an executor (`hass.async_add_executor_job`).
- Registries are plain dicts read on hot paths (every thermostat build, every cycle through the core): keep lookups O(1) and return copies (`get_ui_plugins`) rather than internal structures.
- Do not add a runtime dependency: `dependencies = []` in `pyproject.toml`.
- Event handlers of `PluginClimate` run in an executor thread (`context/pitfalls.md`): keep them free of event-loop-only calls and quick.

## Before handing over

1. The change is backward compatible (`context/contracts.md` table); the frozen sets in `tests/test_backward_compatibility.py` are unchanged unless a core-implemented protocol grew on purpose.
2. Tests written and run (`workflows/testing.md`); exports and `tests/test_package.py` updated.
3. `documentation/en/` and `README.md` updated; the docs describe the current state only.
4. `__version__` bumped when the public surface changed (`workflows/release.md`); say which VT or plugin follow-up is needed.
5. Diff re-read with `git --no-pager diff`; no personal data, plan reference or machine path in code, docs or `.agents/`.
6. Memory checklist of `workflows/memory-maintenance.md`; brief English commit message proposed, nothing committed.
