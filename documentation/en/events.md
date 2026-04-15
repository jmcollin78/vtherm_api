# Events reference

Versatile Thermostat emits Home Assistant events on the event bus for every significant state change. `PluginClimate` subscribes to all of them and routes each to a dedicated handler method.

## How events work

1. A VTherm entity fires a named event on the HA event bus.
2. The event payload always contains an `entity_id` field identifying the source thermostat.
3. `PluginClimate` ignores events whose `entity_id` does not match the linked thermostat.
4. The payload is cached in memory and accessible via `get_event_data(EventType.XXX)`.
5. The matching `handle_*_event(event)` method is called.

## All event types

### SAFETY_EVENT

**HA event name**: `versatile_thermostat_safety_event`  
**Handler**: `handle_safety_event(event)`  
**Triggered when**: The thermostat enters or exits safety mode (e.g., temperature sensor not responding).

### POWER_EVENT

**HA event name**: `versatile_thermostat_power_event`  
**Handler**: `handle_power_event(event)`  
**Triggered when**: The power management feature detects overpowering or resumes normal operation.

### TEMPERATURE_EVENT

**HA event name**: `versatile_thermostat_temperature_event`  
**Handler**: `handle_temperature_event(event)`  
**Triggered when**: A temperature value changes (current temperature, target temperature, or outdoor temperature).

Common payload keys:
- `entity_id` — source thermostat entity ID
- `current_temperature` — current measured temperature
- `target_temperature` — current target temperature

### HVAC_MODE_EVENT

**HA event name**: `versatile_thermostat_hvac_mode_event`  
**Handler**: `handle_hvac_mode_event(event)`  
**Triggered when**: The HVAC mode changes (`heat`, `cool`, `off`, etc.).

Common payload keys:
- `entity_id`
- `hvac_mode` — new mode

### CENTRAL_BOILER_EVENT

**HA event name**: `versatile_thermostat_central_boiler_event`  
**Handler**: `handle_central_boiler_event(event)`  
**Triggered when**: The central boiler state changes (start/stop request).

### PRESET_EVENT

**HA event name**: `versatile_thermostat_preset_event`  
**Handler**: `handle_preset_event(event)`  
**Triggered when**: The active preset changes (`eco`, `comfort`, `boost`, etc.).

Common payload keys:
- `entity_id`
- `preset_mode` — new preset name

### WINDOW_AUTO_EVENT

**HA event name**: `versatile_thermostat_window_auto_event`  
**Handler**: `handle_window_auto_event(event)`  
**Triggered when**: The automatic window detection algorithm detects an open or closed window.

### AUTO_START_STOP_EVENT

**HA event name**: `versatile_thermostat_auto_start_stop_event`  
**Handler**: `handle_auto_start_stop_event(event)`  
**Triggered when**: The auto start/stop feature starts or stops the thermostat.

### TIMED_PRESET_EVENT

**HA event name**: `versatile_thermostat_timed_preset_event`  
**Handler**: `handle_timed_preset_event(event)`  
**Triggered when**: A timed preset activates or expires.

### HEATING_FAILURE_EVENT

**HA event name**: `versatile_thermostat_heating_failure_event`  
**Handler**: `handle_heating_failure_event(event)`  
**Triggered when**: The thermostat detects a heating failure (e.g., temperature not rising as expected).

## Summary table

| EventType constant | HA event name | Handler method |
|---|---|---|
| `SAFETY_EVENT` | `versatile_thermostat_safety_event` | `handle_safety_event` |
| `POWER_EVENT` | `versatile_thermostat_power_event` | `handle_power_event` |
| `TEMPERATURE_EVENT` | `versatile_thermostat_temperature_event` | `handle_temperature_event` |
| `HVAC_MODE_EVENT` | `versatile_thermostat_hvac_mode_event` | `handle_hvac_mode_event` |
| `CENTRAL_BOILER_EVENT` | `versatile_thermostat_central_boiler_event` | `handle_central_boiler_event` |
| `PRESET_EVENT` | `versatile_thermostat_preset_event` | `handle_preset_event` |
| `WINDOW_AUTO_EVENT` | `versatile_thermostat_window_auto_event` | `handle_window_auto_event` |
| `AUTO_START_STOP_EVENT` | `versatile_thermostat_auto_start_stop_event` | `handle_auto_start_stop_event` |
| `TIMED_PRESET_EVENT` | `versatile_thermostat_timed_preset_event` | `handle_timed_preset_event` |
| `HEATING_FAILURE_EVENT` | `versatile_thermostat_heating_failure_event` | `handle_heating_failure_event` |

## Firing events in tests

You can fire events directly on the event bus to simulate VTherm behavior in tests:

```python
hass.bus.async_fire(
    EventType.TEMPERATURE_EVENT.value,
    {
        "entity_id": "climate.living_room",
        "current_temperature": 20.5,
        "target_temperature": 21.0,
    },
)
```

After the event is handled:
- `plugin.last_event_type` is `EventType.TEMPERATURE_EVENT`
- `plugin.get_event_data(EventType.TEMPERATURE_EVENT)` returns the full payload dict
