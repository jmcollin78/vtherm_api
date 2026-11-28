# Decisions

Adopted and rejected approaches, with the reason. Do not re-propose a rejected idea without new evidence. One entry each; rewrite an entry when the code changes.

## Adopted

- **Structural protocols, not base classes.** Every contract is a `@runtime_checkable` `Protocol` so a plugin depends on this package only and needs no VT import; duck typing keeps old plugins working. Cost: `isinstance` checks presence, not signatures (`context/pitfalls.md`).
- **One optional protocol per capability.** A new capability is a separate protocol (`InterfaceCommandReceiptScheduler`, `InterfaceTemperatureTimestampRuntime`, `InterfaceSetpointModifier`, hooks...) detected by the core or the plugin with `hasattr` or `isinstance`; the base protocol stays unchanged so implementations written earlier keep satisfying it. `tests/test_backward_compatibility.py` freezes the base member sets and proves it with legacy implementations.
- **Core-implemented protocols may grow.** `InterfaceThermostatRuntime` can take new members because only VT implements it; VT implements them before raising its minimum requirement, and plugin test doubles must add them. Plugin-implemented protocols never grow.
- **Hooks notify; dedicated contracts modify.** The underlying hooks cannot alter or cancel a core command. A change goes through a contract whose name says so: setpoint modifier, calibration offset modifier, valve write hook. Keeps each plugin's power explicit and auditable.
- **Chains in factory-name order.** The calibration and valve write chains run over the managers in the alphabetical order of their factory names (`VThermAPI.get_feature_manager_factories`); each gets the value left by the previous one; `None` keeps the value. Deterministic without a priority field.
- **Core stays in charge on failure.** An exception, an invalid value or a hook timeout is logged and the core continues with the value it had; a hook is bounded by `UNDERLYING_HOOK_TIMEOUT_SEC`. A plugin bug must not stop heating.
- **Valve takeover is a decision, not a write.** The valve write hook returns a `ValveWriteDecision` at once (`handled`, `settle_sec`); the plugin runs its own sequence in a task, so a timeout cannot race the core write. Recalibration writes, priming and `over_valve` are out of scope on purpose (the recalibration must travel the full stroke).
- **Receipts describe scheduler commands.** `request_id` is opaque to the scheduler; receipts say what the scheduler applied, not measured power, and do not cover cancellation, OFF or load shedding. Upstream changes to the request (safety, output limit) are not attributed.
- **Freshness clocks are optional and weak.** The temperature timestamps are exposed as an optional runtime extension and documented as freshness clocks that can change without a new measurement, so no plugin treats them as observation ids.
- **Inhibition is a two-operation facade.** `set_inhibition` / `unset_inhibition` (plus `is_inhibition_started`) delegate to the core entity; the plugin owns detection and its status, the core owns state, command gate and reconciliation. There is no provider, factory, status, policy or source-configuration surface and no Home Assistant service.
- **UI plugin registry is passive.** It validates structure and uniqueness and keeps registration order; the dashboard owns every interpretation (URL, version constraint, reserved ids, dependencies, load order). An equal re-registration is a no-op so a setup retry or several config entries work; a conflicting one raises. `src/vtherm_api/ui_plugin.py` imports no Home Assistant module.
- **Singleton in `hass.data`.** `VThermAPI` is created lazily by `get_vtherm_api(hass)`; integrations get it from there. There is no `add_entry` / `remove_entry`.
- **Log collector always records.** `VThermLogger` feeds a bounded ring buffer regardless of the configured level so a diagnostic export can contain debug lines the user never enabled; the normal handlers keep the user's level.
- **Docs are executable where cheap.** The UI registry example and its error messages are checked by tests so documentation cannot drift silently.
- **Release by tag with trusted publishing.** A version tag builds, validates tag against built version, publishes to PyPI through an OIDC-gated `pypi` environment, then creates the GitHub release (`workflows/release.md`). No stored PyPI token.

## Rejected or not provided

- Required new members on plugin-implemented protocols: they would break every released plugin.
- Hooks that silently mutate core commands: use the explicit modifier contracts above.
- Receipts or notifications for cancellation, OFF and shedding, and a timestamped command event stream: not part of the contract; a plugin keeps its own applied-power history.
- Interpreting UI plugin dependencies or versions in the registry: belongs to the dashboard.
- Inhibition provider and registry model in this package: the core and the plugin each keep their own state.
