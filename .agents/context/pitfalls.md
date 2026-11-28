# Pitfalls

Durable traps that cost time and will bite again. One bullet each, by theme. Remove a bullet when the code no longer has the trap.

## Registry and singleton

- `VThermAPI.get_feature_manager(name)` returns a feature manager **factory**; `InterfaceThermostatRuntime.get_feature_manager(name)` returns a **manager** instance. Same name, different object and owner.
- The Home Assistant object is a class attribute (`VThermAPI._hass`): `get_vtherm_api()` without argument returns `None` until some call gave `hass`, and `reset_vtherm_api()` sets it back to `None`. Two hass objects in one process share it. Every test that creates the API resets it in setup and teardown.
- `reset_vtherm_api()` empties the three registries of the instance in place: a consumer still holding the instance sees empty registries.
- `register_*` strips the name used as key, but `get_*` and `unregister_*` of algorithms and feature managers do not strip; `factory.name` itself stays unstripped. Look names up with the stripped value. `unregister_ui_plugin` does strip.
- `link_to_vtherm` and `register_manager` swallow errors per entity (logged) and do nothing when no entity matches (`device_info["model"] == DOMAIN` and `InterfaceThermostat`). `link_to_vtherm` also calls `entity.link_to_vtherm(vtherm)`, which `InterfaceThermostat` does not declare: the target entity must provide it.

## Events and PluginClimate

- `PluginClimate._handle_vtherm_event` is a plain function passed to `hass.bus.async_listen`, so Home Assistant runs it in an executor thread (job typing of `get_hassjob_callable_job_type`). Overridden `handle_*_event` methods and the payload cache run off the event loop: do not call `async_*` Home Assistant APIs from them directly.
- `call_linked_vtherm_action` calls the `climate` domain (`CLIMATE_DOMAIN`), as `tests/test_plugin_climate.py` asserts; `documentation/en/api-reference.md` and `documentation/en/architecture.md` describe the VT `DOMAIN`. The code and tests are the truth; the docs are inconsistent.
- The handler table of `PluginClimate` is built in `__init__` from `self.handle_*` bound methods; a new `EventType` needs its handler and table entry or its events are listened to but dropped.

## Contracts

- Hooks are detected by `hasattr` on the method name and protocols are `runtime_checkable`: `isinstance` verifies member presence only. A hook with a wrong signature, or a sync function where a coroutine is expected, is accepted and fails inside the core (logged, command still sent).
- `InterfaceValveWriteHook.async_before_valve_write` must return its decision at once and run a takeover sequence in a background task: the core cancels the call after `UNDERLYING_HOOK_TIMEOUT_SEC` and then writes itself, racing a write done inside the hook.
- `settle_sec` has no upper bound: a plugin announcing more than its real sequence leaves a drifted valve unrepaired that long.
- Valve recalibration writes cannot be changed or taken over by the valve write hook; a plugin follows them in `async_after_valve_command` with cause `RECALIBRATION`, and must filter on `cause` when it tracks the regulation.
- Setpoint modifier: a move smaller than `regulation_step` is swallowed by the core rounding.
- Receipts and power notifications describe the scheduler command, not measured power; the notification can reach a manager seconds after the actuation, so use its timestamps.
- `is_inhibition_started` returns True for a core that does not expose the property: it cannot tell "not started" from "not supported".
- Rules of a hook live in two places, the module docstring and `documentation/en/api-reference.md`; editing one leaves the other stale.

## Logging

- `VThermLogger.isEnabledFor` is always True: every record of a logger obtained from `get_vtherm_logger` is built and fed to the buffer whatever the configured level (only the normal handler chain honors it). Hot-path log calls cost even at WARNING.
- `get_vtherm_logger` edits `logging.Logger.manager.loggerDict` and re-parents existing children; a logger created earlier with plain `logging.getLogger` under the same name is replaced, not wrapped. `VThermLogHandler.__init__` sets the class-level collector: the last handler created wins.
- Export filters attribute a message to a thermostat through the `<name> - ` prefix of the message; a message without it has no hint and appears in every thermostat export.

## Tests and CI

- `tests/` import the package as `src.vtherm_api` (repo root put on `sys.path` by `tests/conftest.py`), a module object distinct from an installed `vtherm_api`: class-level state is not shared between them.
- `tests/test_package.py` compares `__version__` with `src/vtherm_api.egg-info/PKG-INFO` when that folder exists, else with the installed metadata. After changing `__version__`, run `python -m pip install -e .` again or the test fails on stale metadata.
- `tests/test_api_temperature_timestamps.py` is excluded by `collect_ignore` in `tests/conftest.py`: it needs the helper modules `commons` and `test_inhibition` of VT's own tests and only runs in the `vtherm` job of `.github/workflows/tests.yml`, after being copied into VT's tests.
- That `vtherm` job runs the whole VT suite (VT `main` branch) against this checkout, replacing the PyPI package: a contract change can fail there even when this repository's tests pass, for instance a core-implemented member VT does not implement yet.
- `tests/test_ui_plugin_registry.py` executes the example that follows the marker `<!-- example: ui-plugin-registry -->` in `documentation/en/api-reference.md` and requires the four error messages in backticks there: keep the marker and the messages when editing that section.
- Async tests need `@pytest.mark.asyncio` (no asyncio mode is configured).

## Packaging

- `requires-python` is `>=3.13` while CI, the devcontainer and the documentation say 3.14: code using 3.14-only features passes CI and breaks 3.13 users.
- Importing any submodule runs `src/vtherm_api/__init__.py`, which imports Home Assistant: `ui_plugin.py` importing nothing from it does not make the package importable without it.
