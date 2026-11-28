# Testing

## Commands

Run from the repository root (config in `pyproject.toml`, `testpaths = ["tests"]`).

| Goal | Command |
| --- | --- |
| Environment | `python -m pip install -r requirements-dev.txt && python -m pip install -e .` (CI does the same; the editable install also refreshes the version metadata read by `tests/test_package.py`) |
| One file | `python -m pytest tests/test_valve_write.py` |
| One test | `python -m pytest tests/test_valve_write.py -k name` |
| Full suite | `python -m pytest` |
| Memory check | `python3 .agents/scripts/check_memory.py` |

Home Assistant is imported by the package and by the tests: the environment needs the pinned version of `requirements-dev.txt`. Import time is noticeable on a slow disk: run the full suite as a background task and wait for its completion notification; never poll.

## Layout

- One file per module or contract: `tests/test_<module>.py`. `tests/conftest.py` only puts the repository root on `sys.path` and excludes `tests/test_api_temperature_timestamps.py`.
- Tests import `from src import vtherm_api` / `from src.vtherm_api... import ...`.
- `tests/test_backward_compatibility.py`: frozen member sets of every base protocol, signatures, exports, legacy implementations (scheduler, handler, factories, feature manager) that must still satisfy the protocols and must not satisfy the optional ones.
- `tests/test_package.py`: exports of `__all__` and version consistency.
- `tests/test_ui_plugin_registry.py`: also executes the documentation example and checks the documented error messages.
- Asynchronous tests: `@pytest.mark.asyncio` on each (strict mode, nothing configured globally).

## Fixtures and doubles

- No real Home Assistant: a hass is a `SimpleNamespace(data={DOMAIN: {}}, config=SimpleNamespace(time_zone="UTC"))`, or a `MagicMock` with `hass.bus.async_listen` returning a cancel function and `hass.services.async_call` an `AsyncMock`. A climate component is `SimpleNamespace(entities=[...])` under `hass.data["climate"]`.
- An API fixture resets the singleton before and after: `VThermAPI.reset_vtherm_api()`; `VThermAPI.get_vtherm_api(hass)`; the clock is overridden with `api._set_now(...)`.
- Runtime doubles are built from `InterfaceThermostatRuntime.__protocol_attrs__` (see `tests/test_thermostat_runtime.py`, `tests/test_temperature_timestamps.py`) so a new protocol member is noticed.
- Log tests use `VThermLogHandler` with records built by hand; the download view is tested with a temporary folder (`tests/test_log_download_endpoint.py`).

## What to test

- A new contract: payload immutability (`FrozenInstanceError`), defaults, the protocol with a conforming and a non-conforming double, the `hasattr` detection, the export, and a legacy implementation that lacks it.
- A registry or facade change: valid input, each documented error, idempotence, order, effect of `reset_vtherm_api`.
- A change to a base protocol or signature: the frozen sets in `tests/test_backward_compatibility.py` must fail first; change them only when the growth is intended and core-implemented.
- Integration with VT is checked by CI, not locally: the `vtherm` job of `.github/workflows/tests.yml` runs VT's suite against this checkout (`context/pitfalls.md`).
