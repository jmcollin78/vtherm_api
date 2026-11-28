# Architecture

Flat package `src/vtherm_api/`: one module per contract family, no sub-packages, no I/O except the log export and the log download view. Contracts are protocols and frozen dataclasses; the only stateful objects are `VThermAPI`, `PluginClimate` and the log handler.

## Module map

| Module | Role |
| --- | --- |
| `src/vtherm_api/__init__.py` | Public exports (`__all__`) and `__version__` (the version source). |
| `src/vtherm_api/interfaces.py` | Base protocols: `InterfaceThermostat`, `InterfaceFeatureManager`, `InterfaceThermostatRuntime`, `InterfaceTemperatureTimestampRuntime`, `InterfaceCycleScheduler`, `InterfacePropAlgorithmHandler`, `InterfacePropAlgorithmFactory`, `InterfaceFeatureManagerFactory`, and the dataclass `ValveDiagnosticState`. The module docstring states the shared-clock rule for managers. |
| `src/vtherm_api/vtherm_api.py` | `VThermAPI`: singleton in `hass.data[DOMAIN]`, the three registries (algorithms, feature manager factories, UI plugins), the inhibition facade, `link_to_vtherm`, `register_manager`. |
| `src/vtherm_api/plugin_climate.py` | `PluginClimate`: subscribes to the ten VT events for one linked thermostat, caches the last payload per event type, forwards climate service calls. |
| `src/vtherm_api/command_receipt.py` | Optional scheduler extension `InterfaceCommandReceiptScheduler`, `AppliedCommandReceipt`, `CommandReceiptKind`, `CommandAlteration`. |
| `src/vtherm_api/underlying_hooks.py` | Three optional manager hooks (HVAC mode before, valve command after, power notification) and their payloads `ValveCommand`, `ValveCommandCause`, `UnderlyingPowerCommand`, `PowerCommandKind`. |
| `src/vtherm_api/valve_write.py` | Optional manager hook that may change or take over a valve write: `InterfaceValveWriteHook`, `ValveWriteRequest`, `ValveWriteDecision`. Imports `ValveCommandCause` from `underlying_hooks`. |
| `src/vtherm_api/setpoint_modifier.py` | Optional manager hook `InterfaceSetpointModifier` (regulated temperature). |
| `src/vtherm_api/calibration_modifier.py` | Optional manager hook `InterfaceCalibrationOffsetModifier` and `CalibrationOffsetRequest`. |
| `src/vtherm_api/ui_plugin.py` | `UiPlugin` dataclass, `build_ui_plugin` (validation), error message constants. Imports no Home Assistant module on purpose. |
| `src/vtherm_api/inhibition.py` | `InhibitionNotStartedError` (a `HomeAssistantError`). |
| `src/vtherm_api/const.py` | `DOMAIN`, `VTHERM_API_NAME`, `UNDERLYING_HOOK_TIMEOUT_SEC`, `EventType` enum, `NowClass` (clock, test override), `get_tz`. |
| `src/vtherm_api/commons_type.py` | `ConfigData` alias used by `interfaces.py`. |
| `src/vtherm_api/log_collector.py` | `VThermLogger`, `VThermLogHandler` (ring buffer), `get_vtherm_logger`, `write_event_log`, `async_export_logs`, `async_register_log_download_endpoint` (HTTP view; not exported at the package root). |

Main import edges (most modules also import `log_collector`): `command_receipt` -> `interfaces`; `valve_write` -> `underlying_hooks`; `vtherm_api` -> `interfaces`, `plugin_climate`, `ui_plugin`, `log_collector`, `const`. Keep it acyclic.

## Where do I change X

| Change | Files (all in the same change set) |
| --- | --- |
| A new optional manager hook or scheduler extension | a new module (or the matching existing one) with the protocol, payload dataclasses and the contract rules in the module docstring; `src/vtherm_api/__init__.py` (import and `__all__`); `documentation/en/api-reference.md`; tests (see `workflows/testing.md`). Procedure: `context/contracts.md`. |
| A member on a core-implemented protocol | `src/vtherm_api/interfaces.py`, the frozen member sets in `tests/test_backward_compatibility.py`, api-reference. Requires VT to implement it first. |
| A new VT event type | `src/vtherm_api/const.py::EventType`, a `handle_*_event` method and a `_handlers` entry in `src/vtherm_api/plugin_climate.py::PluginClimate`, `documentation/en/events.md`, `tests/test_plugin_climate.py`. `link_to_vtherm` listens to every `EventType` member automatically. |
| UI plugin declaration rules or messages | `src/vtherm_api/ui_plugin.py`, `src/vtherm_api/vtherm_api.py::VThermAPI.register_ui_plugin`, the error list and the example of api-reference (both are checked by `tests/test_ui_plugin_registry.py`). |
| Inhibition operations | `src/vtherm_api/vtherm_api.py::VThermAPI.set_inhibition` and `_get_inhibition_thermostat`, `src/vtherm_api/inhibition.py`, `tests/test_inhibition_api.py`. |
| Log buffer, filters, export, download view | `src/vtherm_api/log_collector.py`, `tests/test_log_collector.py`, `tests/test_log_download_endpoint.py`. |
| Version | `src/vtherm_api/__init__.py::__version__` only (`workflows/release.md`). |

## Documentation map

- `documentation/en/api-reference.md` (about 800 lines): one section per public class, protocol and hook; the contract rules of each hook are mirrored from the module docstring. Largest file; read it by heading with `grep -n '^#'`.
- `documentation/en/architecture.md`, `events.md`, `overview.md`, `getting-started.md`, `testing.md`, `documentation/en/guides/*.md`: lifecycle diagrams, event payloads, recipes for plugin authors.
- `README.md`: feature summary and installation.

## Tests map

One test file per module or contract: `tests/test_<module>.py` (receipts, hooks, valve write, calibration, setpoint, UI registry, inhibition, log collector, log download, plugin climate, registries, runtime, timestamps). `tests/test_backward_compatibility.py` freezes the public surface; `tests/test_package.py` checks exports and the version. `tests/test_api_temperature_timestamps.py` is not run here (see `context/pitfalls.md`).

## Large files

`src/vtherm_api/log_collector.py` (about 570 lines: logger swap, ring buffer, HTTP view, export), `src/vtherm_api/interfaces.py` (about 425), `src/vtherm_api/vtherm_api.py` (about 320), `tests/test_log_collector.py`, `documentation/en/api-reference.md`. Read by symbol with `grep -n '^class \|^def \|    def '`.
