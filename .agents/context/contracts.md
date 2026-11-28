# Contracts

Source of truth for the rules of each contract: the module docstring (`src/vtherm_api/*.py`), mirrored by `documentation/en/api-reference.md`. This file gives the map: who implements what, when it is called, and what may change. "Core" is VT; "plugin" is any integration depending on this package.

## Compatibility rules (all contracts)

| Kind | Implemented by | May change without breaking |
| --- | --- | --- |
| Plugin-implemented protocol (`InterfaceFeatureManager`, `InterfaceFeatureManagerFactory`, `InterfacePropAlgorithmHandler`, `InterfacePropAlgorithmFactory`, every optional hook protocol) | plugin | Nothing required: no new member, no changed signature. Add a new optional protocol instead. |
| Core-implemented protocol (`InterfaceThermostatRuntime`, `InterfaceCycleScheduler`) | core | New members, only after the core implements them; the core then raises its minimum requirement. Plugin test doubles must gain the member. |
| Optional extension of a core-implemented protocol | core, optionally | Own protocol extending the unchanged base (`InterfaceTemperatureTimestampRuntime`, `InterfaceCommandReceiptScheduler`); a plugin detects it with `isinstance` or `hasattr` and falls back. |
| Payload dataclass (`ValveCommand`, `ValveWriteRequest`, `UnderlyingPowerCommand`, `AppliedCommandReceipt`, ...) | built by the core, read by plugins | New field with a default, placed last. Never rename, reorder or retype a field. |
| `StrEnum` of causes and kinds | core emits | New values in a minor version; a consumer must ignore a value it does not know. |
| `VThermAPI` method | plugin calls | New optional parameters only; keep the signature checked by `tests/test_backward_compatibility.py`. |

`isinstance` against a `runtime_checkable` protocol checks member presence, not signatures or async-ness: a wrong signature is not caught by it.

## How to add a contract compatibly

1. Choose the side: plugin-implemented (new optional protocol, detected by the core) or core-implemented (new member or optional extension of the runtime or scheduler).
2. Write the protocol and its payload dataclasses (`frozen=True, slots=True`, defaults on anything added later) in the matching module or a new one. The module docstring lists the rules: who calls, when, ordering, sync or async, timeout, error handling, what is not covered.
3. Export every public name in `src/vtherm_api/__init__.py` (import and `__all__`).
4. Tests: a behaviour file for the contract; an assertion in `tests/test_package.py`; in `tests/test_backward_compatibility.py` a legacy implementation that lacks the new capability and still satisfies the base protocols, and unchanged base member sets.
5. Document in `documentation/en/api-reference.md` (and the README feature list); bump `__version__` (`workflows/release.md`).
6. Publish this package first, then VT implements or calls it and raises its minimum, then plugins use it.

## Registries and singleton (`src/vtherm_api/vtherm_api.py::VThermAPI`)

- One instance in `hass.data[DOMAIN][VTHERM_API_NAME]`, created on first `get_vtherm_api(hass)`. The Home Assistant object is stored on the class: `api.hass` and `api.now` read it, one per process.
- Three independent registries: proportional algorithms (`register_prop_algorithm`), feature manager factories (`register_feature_manager`), UI plugins (`register_ui_plugin`). Same name in two registries is fine.
- Algorithm and factory registration replaces an existing entry of the same stripped name and rejects an empty name (`ValueError`). Unregistering an unknown name is a no-op.
- `get_feature_manager_factories()` returns the factories sorted by name: this order is the call order of the calibration and valve write chains, as their docstrings state. The setpoint modifier order is VT behaviour (managers in registration order); managers added through `VThermAPI.register_manager` are outside the factory order.
- `reset_vtherm_api()` clears the three registries in place, removes the instance and the class-level `hass`. It exists for tests and unload.
- `InterfaceThermostat` is only a structural check (name, unique id, device info, `register_manager`) on climate entities. `register_manager(manager)` registers one manager instance on every climate entity whose `device_info["model"] == DOMAIN` and that satisfies `InterfaceThermostat`. `link_to_vtherm(vtherm, entity_id)` finds the matching entity and calls its own `link_to_vtherm`. Neither raises when nothing matches.

## Feature manager (`InterfaceFeatureManager`, `InterfaceFeatureManagerFactory`)

- Implemented by a plugin; owned and driven by the core. Two ways in: a factory registered in `VThermAPI` (core builds one manager per thermostat for which `supports(runtime)` is true, then `thermostat.register_manager(manager)`), or a single instance through `VThermAPI.register_manager`.
- Lifecycle driven by the core: `post_init(entry_infos)`, `start_listening`, `refresh_state` (each control cycle), `restore_state`, `stop_listening`; `add_listener` collects callbacks to remove on stop.
- `is_configured` gates every optional hook: the core calls a hook only on a configured manager.
- Time-based state uses `InterfaceThermostatRuntime.now`, never a local clock (module docstring of `src/vtherm_api/interfaces.py`).

## Proportional algorithm (`InterfacePropAlgorithmFactory`, `InterfacePropAlgorithmHandler`)

- The plugin registers a factory by name; the core calls `create(runtime)` when a thermostat uses that algorithm and drives the handler: `init_algorithm`, `async_added_to_hass`, `async_startup`, `control_heating(timestamp, force)` every iteration, `on_state_changed(changed)`, `on_scheduler_ready(scheduler)`, `remove`. `should_publish_intermediate` tells the core whether intermediate states may be published.

## Thermostat runtime (`InterfaceThermostatRuntime`, core-implemented)

- Read view (temperatures, target, mode, cycle, power, valve diagnostics, entry infos) plus actions: `async_set_underlying_fan_mode`, `async_underlying_entity_turn_off`, `async_control_heating`, `async_request_state_refresh`, `update_custom_attributes`, `async_write_ha_state`, `send_event`, `get_feature_manager(name)`.
- `async_request_state_refresh` is for transitions, not per cycle; a not-ready thermostat logs and returns.
- `vtherm_hvac_modes` may hold core-specific objects: compare their `str()`.
- `InterfaceTemperatureTimestampRuntime` (optional): `last_temperature_measure` and `last_ext_temperature_measure` are freshness clocks that can change without a new measurement; they are neither acquisition times nor observation ids.

## Cycle scheduler and receipts (`InterfaceCycleScheduler`, `InterfaceCommandReceiptScheduler`)

- Base: `start_cycle(hvac_mode, on_percent, force)`, `cancel_cycle`, start and end callbacks, `is_cycle_running`.
- Optional receipts (`src/vtherm_api/command_receipt.py`): the plugin passes an opaque `request_id` to `start_cycle`; for each command the scheduler really applies it awaits registered coroutine callbacks with an `AppliedCommandReceipt` echoing the id. A callback exception is logged and does not break the cycle.
- Not covered: cancellation, HVAC OFF, power shedding, a switch request stored as pending (receipt comes when applied). A receipt describes the scheduler command, not measured power. The requested value may already have been changed upstream by safety or an output limit.

## Optional manager hooks (detected by `hasattr` on the method name)

| Contract | Method | Called | Effect |
| --- | --- | --- | --- |
| `InterfaceSetpointModifier` (`setpoint_modifier.py`) | `adjust_regulated_temperature(desired, regulation_step, command_cause)` | Each computation of the regulated temperature of an `over_climate`, before the device offset, rounding and delta filter | Sync, returns the temperature or `None` to keep. A move smaller than `regulation_step` is swallowed by the core rounding. |
| `InterfaceCalibrationOffsetModifier` (`calibration_modifier.py`) | `adjust_calibration_offset(request)` | `over_climate` calibration mode, after the offset is computed, before comparison with the current one | Sync chain in factory-name order; `None` keeps; the core clamps to the min and max offset, rounds to the step, writes only on change. |
| `InterfaceUnderlyingHvacModeHook` (`underlying_hooks.py`) | `async_before_underlying_hvac_mode(climate_entity_id, hvac_mode, current_hvac_mode, command_cause)` | Just before `climate.set_hvac_mode` is sent | Notification only. |
| `InterfaceValveCommandHook` | `async_after_valve_command(command)` | After opening and closing degrees were sent (also after a plugin write and after a recalibration write) | Notification only. |
| `InterfaceUnderlyingPowerHook` | `async_on_underlying_power(command)` | Cycle start, valve update, cycle stop, per underlying | Notification only; use the command timestamps, not the reception time. |
| `InterfaceValveWriteHook` (`valve_write.py`) | `async_before_valve_write(request)` | Before each `valve_regulation` write, including repairs; not for recalibration, priming, `over_valve`, or when inhibition blocks the write | May change the opening, take the write over (`handled=True`) and announce `settle_sec`. |

Shared rules: the async hooks are awaited by the core and cut after `UNDERLYING_HOOK_TIMEOUT_SEC` (10 s); an exception or timeout is logged and the core command still goes out; notifications fire only for a command really sent (not when inhibition blocks it, the mode is already in place, or load shedding refuses). Hooks must return quickly and start slow work in a task. An enum value or cause a hook does not know must be ignored.

## Inhibition facade (`VThermAPI.set_inhibition`, `unset_inhibition`, `is_inhibition_started`)

- The plugin owns detection and its own status; the core owns the inhibition state, the command gate, the entry stop and the exit reconciliation. `stop_underlyings` (a `bool`, else `TypeError`) only authorizes the one-time entry stop.
- Call `unset_inhibition` only after the plugin confirmed its inactive state.
- The target is found among the entities of the climate component by entity id and must implement `async_set_inhibition(bool)` and `async_unset_inhibition()`. Errors: `ValueError` (blank id), `LookupError` (no component or entity), `TypeError` (no inhibition support), `InhibitionNotStartedError` before the core restored its state at startup.
- `is_inhibition_started` reads the optional property `is_inhibition_started` of the entity; a core without it counts as started.

## UI plugin registry (`register_ui_plugin`, `unregister_ui_plugin`, `get_ui_plugins`)

- Passive: validates structure and identifier uniqueness only; keeps registration order; never sorts nor interprets URL, version constraint, reserved `core` and `core_*` ids or dependencies (the dashboard does, on each build of its list).
- Registering an equal declaration again is a no-op that keeps the place; a different declaration with the same stripped id raises `ValueError`. Identifiers are stripped; `js_url` and `dashboard_version` are kept as given. `get_ui_plugins` returns a new list. Call from the event loop.

## Events and `PluginClimate` (`src/vtherm_api/plugin_climate.py`)

- The core fires the ten `EventType` events on the Home Assistant bus; each payload holds `entity_id`. After `link_to_vtherm(vtherm)`, `PluginClimate` ignores events of other entities, caches the last payload per type (`get_event_data`) and calls the matching `handle_*_event`, empty by default: a plugin subclasses it and overrides the handlers it needs.
- `call_linked_vtherm_action(name, data, ...)` calls the Home Assistant `climate` domain service `name` targeted at the linked entity; no link raises `RuntimeError`; a failing call is logged and returns `None`.

## Logging helpers (`src/vtherm_api/log_collector.py`)

- `get_vtherm_logger(name)` swaps the logger for a `VThermLogger` that always builds records and always feeds the ring buffer of the `VThermLogHandler` (age and size bounded), while normal handlers still honor the configured level. `write_event_log(logger, vtherm, message)` writes the recognizable event line. `async_export_logs` writes a file under the Home Assistant config `www/versatile_thermostat` in an executor, then creates a persistent notification with a signed link served by the view of `async_register_log_download_endpoint` (authenticated, filename pattern checked against traversal).
- Log messages shaped `<thermostat name> - ...` are attributed to that thermostat by the filters; other messages are kept for every thermostat filter.
