# API Reference

## VThermAPI

**Module**: `vtherm_api.vtherm_api`  
**Type**: Singleton class stored in `hass.data[DOMAIN][VTHERM_API_NAME]`

### Class methods

#### `VThermAPI.get_vtherm_api(hass=None) → VThermAPI | None`

Get or create the singleton instance.

- If `hass` is provided, creates the instance if it does not exist yet and stores it in `hass.data`.
- If `hass` is `None`, returns the existing instance or `None`.

```python
# In async_setup_entry — always pass hass to create on first call
api = VThermAPI.get_vtherm_api(hass)

# In async_unload_entry — no hass needed, just retrieve
api = VThermAPI.get_vtherm_api()
```

#### `VThermAPI.reset_vtherm_api() → None`

Destroy the singleton and clear all registries. Primarily useful in tests.

```python
def teardown_function():
    VThermAPI.reset_vtherm_api()
```

### Properties

| Property | Type | Description |
|---|---|---|
| `hass` | `HomeAssistant` | The Home Assistant instance passed at creation. |
| `name` | `str` | Always returns `"VThermAPI"`. |
| `now` | `datetime` | Timezone-aware current datetime from the HA clock. |

### Instance methods

#### `add_entry(entry: ConfigEntry) → None`

Register a config entry with the API.

#### `remove_entry(entry: ConfigEntry) → None`

Remove a previously registered config entry.

#### `register_prop_algorithm(factory: InterfacePropAlgorithmFactory) → None`

Register a proportional algorithm factory. If a factory with the same name already exists, it is replaced.

#### `unregister_prop_algorithm(name: str) → None`

Remove a registered factory by name. No-op if the name is not found.

#### `get_prop_algorithm(name: str) → InterfacePropAlgorithmFactory | None`

Look up a factory by name. Returns `None` if not registered.

#### `list_prop_algorithms() → list[str]`

Return a sorted list of all registered algorithm names.

#### `link_to_vtherm(vtherm, plugin_vtherm_entity_id: str) → None`

Search the Home Assistant climate component for a `PluginClimate` entity whose `entity_id` matches `plugin_vtherm_entity_id`, then call `plugin.link_to_vtherm(vtherm)` on it.

Use this helper only when the plugin climate is already registered as an HA entity. For direct linking in tests or custom setups, call `plugin.link_to_vtherm(vtherm)` directly.

#### `register_manager(manager: InterfaceFeatureManager) → None`

Register a feature manager across all VTherm thermostat entities found in the Home Assistant climate component.

Only entities that implement `InterfaceThermostat` and expose `device_info["model"] == DOMAIN` receive the manager.

### Testing helper

#### `_set_now(now: datetime) → None`

Override the value returned by `api.now`. Useful for time-based test scenarios.

---

## PluginClimate

**Module**: `vtherm_api.plugin_climate`

An event listener and service forwarder bound to exactly one linked VTherm thermostat entity.

### Constructor

```python
plugin = PluginClimate(hass)
```

### Linking

#### `link_to_vtherm(vtherm: Any) → None`

Bind the plugin to a thermostat object.

1. Removes any previously registered listeners.
2. Stores `vtherm` in `linked_vtherm`.
3. Registers one HA event listener for every `EventType`.

Only events whose `data["entity_id"]` matches `linked_vtherm.entity_id` are processed.

#### `remove_listeners() → None`

Unregister all Home Assistant event listeners. Call this when the integration unloads.

#### `linked_vtherm` *(property)*

Returns the currently linked thermostat object, or `None` if not linked.

### Event data

#### `last_event_type` *(property)*  → `EventType | None`

The type of the last event that was handled.

#### `get_event_data(event_type: EventType) → dict[str, Any]`

Return the most recent payload received for the given event type. Returns an empty `{}` if no event of that type has been seen yet.

### Event handlers

All event handlers receive the raw Home Assistant `Event` object. Override the methods you need in a subclass — the default implementations are empty.

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

#### `handle_vtherm_event(event: Event) → None`

Low-level entrypoint called by every registered listener. Filters by `entity_id`, caches the payload, updates `last_event_type`, then dispatches to the matching `handle_*` method. Exposed publicly to allow direct invocation in tests.

### Action forwarding

#### `await call_linked_vtherm_action(action_name, action_data=None, blocking=False, context=None, return_response=False) → Any`

Forward a service call to the linked VTherm thermostat.

Internally calls:
```python
await hass.services.async_call(
    domain=DOMAIN,               # "versatile_thermostat"
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

All interfaces are defined as `@runtime_checkable` `Protocol` classes in `vtherm_api.interfaces`.

### InterfaceThermostat

Minimal contract expected of a VTherm thermostat entity.

| Member | Type | Description |
|---|---|---|
| `name` | `str` property | Human-readable name. |
| `unique_id` | `str` property | Unique entity identifier. |
| `device_info` | `DeviceInfo \| None` property | HA device info. Must have `model == DOMAIN` for manager registration. |
| `register_manager(manager)` | method | Receives a feature manager instance. |

### InterfaceFeatureManager

Contract for a feature manager that extends thermostat behavior.

| Member | Signature | Description |
|---|---|---|
| `name` | `str` property | Logical name of the manager. |
| `hass` | `HomeAssistant` property | Home Assistant instance. |
| `is_configured` | `bool` property | Whether the manager is properly configured. |
| `is_detected` | `bool` property | Whether the managed condition is currently active. |
| `post_init(entry_infos)` | `(dict) → None` | Called with merged config data after creation. |
| `start_listening(force)` | `async (bool) → None` | Subscribe to events. |
| `stop_listening()` | `() → bool \| None` | Unsubscribe all listeners. |
| `refresh_state()` | `async () → bool` | Refresh internal state. Returns `True` if state changed. |
| `restore_state(old_state)` | `(Any) → None` | Restore from a previous HA state. |
| `add_listener(func)` | `(CALLBACK_TYPE) → None` | Register a cleanup callback. |

### InterfaceThermostatRuntime

Runtime view of a VTherm thermostat, exposed to proportional algorithm plugins.

**Writable attributes:**

| Attribute | Type | Description |
|---|---|---|
| `prop_algorithm` | `Any` | The active proportional algorithm object. |
| `minimal_activation_delay` | `int` | Minimum on-time in seconds. |
| `minimal_deactivation_delay` | `int` | Minimum off-time in seconds. |

**Read-only properties:**

| Property | Type | Description |
|---|---|---|
| `hass` | `HomeAssistant` | Home Assistant instance. |
| `entity_id` | `str` | Entity identifier. |
| `name` | `str` | Human-readable name. |
| `unique_id` | `str` | Unique identifier. |
| `entry_infos` | `ConfigData \| dict` | Merged configuration data. |
| `current_temperature` | `float \| None` | Current measured temperature. |
| `current_outdoor_temperature` | `float \| None` | Current outdoor temperature. |
| `target_temperature` | `float \| None` | Current target temperature. |
| `last_temperature_slope` | `float \| None` | Rate of temperature change. |
| `vtherm_hvac_mode` | `str \| None` | Current HVAC mode. |
| `hvac_action` | `str \| None` | Current HVAC action. |
| `hvac_off_reason` | `str \| None` | Reason the HVAC is off. |
| `cycle_min` | `int` | Cycle duration in minutes. |
| `cycle_scheduler` | `InterfaceCycleScheduler \| None` | The cycle scheduler instance. |
| `is_device_active` | `bool` | Whether the underlying device is currently on. |
| `is_overpowering_detected` | `bool` | Whether overpowering is detected. |

**Methods:**

| Method | Signature | Description |
|---|---|---|
| `async_underlying_entity_turn_off()` | `async () → None` | Turn off the underlying heating device. |
| `async_control_heating(timestamp, force)` | `async (datetime\|None, bool) → bool` | Run one heating control iteration. |
| `update_custom_attributes()` | `() → None` | Refresh custom state attributes. |
| `async_write_ha_state()` | `() → None` | Push state to Home Assistant. |

### InterfacePropAlgorithmHandler

Lifecycle contract for a proportional algorithm handler bound to one thermostat.

| Method | Signature | Description |
|---|---|---|
| `init_algorithm()` | `() → None` | Initialize algorithm state. Called at creation. |
| `async_added_to_hass()` | `async () → None` | Called when the thermostat entity is added to HA. |
| `async_startup()` | `async () → None` | Called after thermostat initialization. |
| `remove()` | `() → None` | Release resources. Called on unload. |
| `control_heating(timestamp, force)` | `async (datetime\|None, bool) → None` | Execute one control iteration. |
| `on_state_changed()` | `async () → None` | React to thermostat state change. |
| `on_scheduler_ready(scheduler)` | `(InterfaceCycleScheduler) → None` | Bind the handler to the cycle scheduler. |
| `should_publish_intermediate()` | `() → bool` | Whether VTherm should publish intermediate states. |

### InterfacePropAlgorithmFactory

Factory for registering a proportional algorithm implementation.

| Member | Signature | Description |
|---|---|---|
| `name` | `str` property | Unique algorithm identifier. |
| `create(thermostat)` | `(InterfaceThermostatRuntime) → InterfacePropAlgorithmHandler` | Create and return a handler bound to the thermostat. |

### InterfaceCycleScheduler

Contract exposed by the VTherm cycle scheduler.

| Member | Signature | Description |
|---|---|---|
| `is_cycle_running` | `bool` property | Whether a cycle is currently active. |
| `register_cycle_start_callback(callback)` | `(Callable) → None` | Register a callback fired at cycle start. |
| `register_cycle_end_callback(callback)` | `(Callable) → None` | Register a callback fired at cycle end. |
| `start_cycle(hvac_mode, on_percent, force)` | `async (Any, float, bool) → None` | Start or update a cycle. |
| `cancel_cycle()` | `async () → None` | Cancel the current cycle. |

---

## Constants and EventType

**Module**: `vtherm_api.const`

### Domain constants

| Constant | Value | Description |
|---|---|---|
| `DOMAIN` | `"versatile_thermostat"` | VTherm HA domain. Used as service domain. |
| `VTHERM_API_NAME` | `"vtherm_api"` | Key under `hass.data[DOMAIN]` where the singleton lives. |
| `DEVICE_MANUFACTURER` | `"JMCOLLIN"` | Device manufacturer string. |
| `DEVICE_MODEL` | `"Versatile Thermostat"` | Device model string. |
| `CONF_NAME` | `"name"` | Config entry name key. |

### EventType enum

```python
from vtherm_api.const import EventType

EventType.SAFETY_EVENT           # "versatile_thermostat_safety_event"
EventType.POWER_EVENT            # "versatile_thermostat_power_event"
EventType.TEMPERATURE_EVENT      # "versatile_thermostat_temperature_event"
EventType.HVAC_MODE_EVENT        # "versatile_thermostat_hvac_mode_event"
EventType.CENTRAL_BOILER_EVENT   # "versatile_thermostat_central_boiler_event"
EventType.PRESET_EVENT           # "versatile_thermostat_preset_event"
EventType.WINDOW_AUTO_EVENT      # "versatile_thermostat_window_auto_event"
EventType.AUTO_START_STOP_EVENT  # "versatile_thermostat_auto_start_stop_event"
EventType.TIMED_PRESET_EVENT     # "versatile_thermostat_timed_preset_event"
EventType.HEATING_FAILURE_EVENT  # "versatile_thermostat_heating_failure_event"
```

### Utility functions

#### `get_tz(hass: HomeAssistant) → tzinfo`

Return the timezone configured in Home Assistant.

#### `NowClass.get_now(hass: HomeAssistant) → datetime`

Return the current timezone-aware datetime. Can be overridden for testing.

---

## Common types

**Module**: `vtherm_api.commons_type`

```python
ConfigData = MappingProxyType[str, Any]
```

Used throughout the interfaces as the type for config entry data.
