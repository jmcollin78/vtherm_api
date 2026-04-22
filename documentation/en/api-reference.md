# API Reference

## VThermAPI

**Module**: `vtherm_api.vtherm_api`

Singleton stored in `hass.data[DOMAIN][VTHERM_API_NAME]`.

### Class methods

#### `VThermAPI.get_vtherm_api(hass=None) -> VThermAPI | None`

Get or create the singleton instance.

- If `hass` is provided, the singleton is created on first call and stored in `hass.data`.
- If `hass` is omitted, the existing singleton is returned if already created.

#### `VThermAPI.reset_vtherm_api() -> None`

Reset the singleton and clear the proportional algorithm registry.
Mainly useful in tests.

### Properties

| Property | Type | Description |
|---|---|---|
| `hass` | `HomeAssistant` | Home Assistant instance associated with the singleton |
| `name` | `str` | Always `"VThermAPI"` |
| `now` | `datetime` | Timezone-aware datetime from Home Assistant |

### Instance methods

#### `register_prop_algorithm(factory: InterfacePropAlgorithmFactory) -> None`

Register or replace a proportional algorithm factory by name.

#### `unregister_prop_algorithm(name: str) -> None`

Remove a proportional algorithm factory by name.

#### `get_prop_algorithm(name: str) -> InterfacePropAlgorithmFactory | None`

Return the factory registered for `name`, or `None`.

#### `list_prop_algorithms() -> list[str]`

Return registered factory names in sorted order.

#### `link_to_vtherm(vtherm, plugin_vtherm_entity_id: str) -> None`

Search the Home Assistant climate component for a plugin climate entity matching `plugin_vtherm_entity_id`, then call `plugin.link_to_vtherm(vtherm)`.

This helper is only useful when your plugin climate is itself an HA climate entity.
For many integrations, direct linking through `PluginClimate.link_to_vtherm(...)` is simpler.

#### `register_manager(manager: InterfaceFeatureManager) -> None`

Register a feature manager across VTherm thermostat entities found in the Home Assistant climate component.

Only entities implementing `InterfaceThermostat` and exposing `device_info["model"] == DOMAIN` receive the manager.

#### `_set_now(now: datetime) -> None`

Testing helper that overrides the value returned by `api.now`.

---

## PluginClimate

**Module**: `vtherm_api.plugin_climate`

Helper bound to exactly one linked VTherm thermostat.
It can subscribe to VTherm events, cache the latest payload for each event type, and forward HA service calls to the linked thermostat.

### Constructor

```python
plugin = PluginClimate(hass)
```

### Linking methods

#### `link_to_vtherm(vtherm: Any) -> None`

Link the helper to a VTherm object.

- removes previous listeners
- stores the VTherm reference in `linked_vtherm`
- registers one HA listener for every `EventType`

Only events whose payload `entity_id` matches `linked_vtherm.entity_id` are processed.

#### `remove_listeners() -> None`

Remove all registered HA listeners.

### Properties

#### `linked_vtherm`

Return the currently linked VTherm object, or `None`.

#### `last_event_type`

Return the last handled `EventType`, or `None`.

### Event data helpers

#### `get_event_data(event_type: EventType) -> dict[str, Any]`

Return the most recent payload received for the given event type.
Returns `{}` if no event of that type has been seen yet.

### Event entrypoint

#### `handle_vtherm_event(event: Event) -> None`

Public wrapper around the internal event handling path.
Useful in tests or when invoking the dispatcher manually.

### Event handlers

Override only the handlers you need in a subclass:

| Method | Triggered by |
|---|---|
| `handle_safety_event(event)` | `EventType.SAFETY_EVENT` |
| `handle_power_event(event)` | `EventType.POWER_EVENT` |
| `handle_temperature_event(event)` | `EventType.TEMPERATURE_EVENT` |
| `handle_hvac_mode_event(event)` | `EventType.HVAC_MODE_EVENT` |
| `handle_central_boiler_event(event)` | `EventType.CENTRAL_BOILER_EVENT` |
| `handle_preset_event(event)` | `EventType.PRESET_EVENT` |
| `handle_window_auto_event(event)` | `EventType.WINDOW_AUTO_EVENT` |
| `handle_auto_start_stop_event(event)` | `EventType.AUTO_START_STOP_EVENT` |
| `handle_timed_preset_event(event)` | `EventType.TIMED_PRESET_EVENT` |
| `handle_heating_failure_event(event)` | `EventType.HEATING_FAILURE_EVENT` |

### Action forwarding

#### `await call_linked_vtherm_action(action_name, action_data=None, blocking=False, context=None, return_response=False) -> Any`

Forward a service call to the linked VTherm thermostat.

Internally this becomes:

```python
await hass.services.async_call(
    domain=DOMAIN,
    service=action_name,
    service_data=action_data,
    blocking=blocking,
    context=context,
    target={"entity_id": linked_vtherm.entity_id},
    return_response=return_response,
)
```

Raises `RuntimeError` if no thermostat is linked.

---

## Interfaces

All interfaces are defined as runtime-checkable `Protocol` classes in `vtherm_api.interfaces`.

### InterfaceThermostat

Minimal contract expected of a VTherm thermostat entity.

| Member | Type | Description |
|---|---|---|
| `name` | `str` property | Human-readable name |
| `unique_id` | `str` property | Unique identifier |
| `device_info` | `DeviceInfo | None` property | HA device info |
| `register_manager(manager)` | method | Accepts a feature manager |

### InterfaceFeatureManager

Contract for a feature manager registered through `VThermAPI.register_manager(...)`.

| Member | Signature | Description |
|---|---|---|
| `name` | `str` property | Logical manager name |
| `hass` | `HomeAssistant` property | Home Assistant instance |
| `is_configured` | `bool` property | Whether the manager is configured |
| `is_detected` | `bool` property | Whether the condition is currently detected |
| `post_init(entry_infos)` | `(dict) -> None` | Receive merged config |
| `start_listening(force)` | `async (bool) -> None` | Start subscriptions |
| `stop_listening()` | `() -> bool | None` | Stop subscriptions |
| `refresh_state()` | `async () -> bool` | Refresh internal state |
| `restore_state(old_state)` | `(Any) -> None` | Restore old state |
| `add_listener(func)` | `(CALLBACK_TYPE) -> None` | Register cleanup callbacks |

### InterfaceThermostatRuntime

Runtime view exposed to proportional algorithm handlers.

#### Writable attributes

| Attribute | Type | Description |
|---|---|---|
| `prop_algorithm` | `Any` | Current algorithm object |
| `minimal_activation_delay` | `int` | Minimum activation delay |
| `minimal_deactivation_delay` | `int` | Minimum deactivation delay |

#### Read-only properties

| Property | Type | Description |
|---|---|---|
| `hass` | `HomeAssistant` | Home Assistant instance |
| `entity_id` | `str` | Entity id |
| `name` | `str` | Thermostat name |
| `unique_id` | `str` | Unique id |
| `entry_infos` | `ConfigData | dict` | Merged thermostat config |
| `current_temperature` | `float | None` | Room temperature |
| `current_outdoor_temperature` | `float | None` | Outdoor temperature |
| `target_temperature` | `float | None` | Target temperature |
| `last_temperature_slope` | `float | None` | Latest temperature slope |
| `vtherm_hvac_mode` | `str | None` | VTherm HVAC mode |
| `hvac_action` | `str | None` | HVAC action |
| `hvac_off_reason` | `str | None` | HVAC off reason |
| `cycle_min` | `int` | Cycle length in minutes |
| `cycle_scheduler` | `InterfaceCycleScheduler | None` | Cycle scheduler |
| `is_device_active` | `bool` | Whether the underlying device is on |
| `is_overpowering_detected` | `bool` | Whether power shedding is active |

#### Methods

| Method | Signature | Description |
|---|---|---|
| `async_underlying_entity_turn_off()` | `async () -> None` | Turn off the underlying entities |
| `async_control_heating(timestamp, force)` | `async (datetime | None, bool) -> bool` | Trigger VTherm control |
| `update_custom_attributes()` | `() -> None` | Refresh custom state attributes |
| `async_write_ha_state()` | `() -> None` | Publish state to Home Assistant |

### InterfacePropAlgorithmHandler

Lifecycle contract for one proportional algorithm handler instance.

| Method | Signature | Description |
|---|---|---|
| `init_algorithm()` | `() -> None` | Initialize algorithm state |
| `async_added_to_hass()` | `async () -> None` | Called when entity is added to HA |
| `async_startup()` | `async () -> None` | Called after VTherm startup |
| `remove()` | `() -> None` | Cleanup resources |
| `control_heating(timestamp, force)` | `async (datetime | None, bool) -> None` | Run one control iteration |
| `on_state_changed(changed)` | `async (bool) -> None` | React to thermostat state refreshes and state changes |
| `on_scheduler_ready(scheduler)` | `(InterfaceCycleScheduler) -> None` | Receive scheduler |
| `should_publish_intermediate()` | `() -> bool` | Allow intermediate state publication |

### InterfacePropAlgorithmFactory

Factory registered in `VThermAPI`.

| Member | Signature | Description |
|---|---|---|
| `name` | `str` property | Unique algorithm identifier |
| `create(thermostat)` | `(InterfaceThermostatRuntime) -> InterfacePropAlgorithmHandler` | Create a handler |

### InterfaceCycleScheduler

Contract exposed by the VTherm cycle scheduler.

| Member | Signature | Description |
|---|---|---|
| `is_cycle_running` | `bool` property | Whether a cycle is active |
| `register_cycle_start_callback(callback)` | `(Callable) -> None` | Register cycle start callback |
| `register_cycle_end_callback(callback)` | `(Callable) -> None` | Register cycle end callback |
| `start_cycle(hvac_mode, on_percent, force)` | `async (Any, float, bool) -> None` | Start or update a cycle |
| `cancel_cycle()` | `async () -> None` | Cancel the current cycle |

---

## Constants and EventType

**Module**: `vtherm_api.const`

### Domain constants

| Constant | Value | Description |
|---|---|---|
| `DOMAIN` | `"versatile_thermostat"` | VTherm service domain |
| `VTHERM_API_NAME` | `"vtherm_api"` | Singleton key in `hass.data[DOMAIN]` |

### EventType enum

```python
from vtherm_api.const import EventType

EventType.SAFETY_EVENT
EventType.POWER_EVENT
EventType.TEMPERATURE_EVENT
EventType.HVAC_MODE_EVENT
EventType.CENTRAL_BOILER_EVENT
EventType.PRESET_EVENT
EventType.WINDOW_AUTO_EVENT
EventType.AUTO_START_STOP_EVENT
EventType.TIMED_PRESET_EVENT
EventType.HEATING_FAILURE_EVENT
```
