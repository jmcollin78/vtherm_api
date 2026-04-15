# Guide: Forward actions to VTherm

## Goal

Send a command (service call) to a linked VTherm thermostat from your plugin.

## How it works

`PluginClimate.call_linked_vtherm_action(...)` wraps `hass.services.async_call(...)` and automatically sets the `target` to the linked thermostat's `entity_id`. You do not need to build the target payload yourself.

## Basic usage

```python
# Change the HVAC mode
await plugin.call_linked_vtherm_action(
    "set_hvac_mode",
    action_data={"hvac_mode": "heat"},
)

# Change the target temperature
await plugin.call_linked_vtherm_action(
    "set_target_temperature",
    action_data={"temperature": 19.5},
)

# Change the preset
await plugin.call_linked_vtherm_action(
    "set_preset_mode",
    action_data={"preset_mode": "eco"},
)
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `action_name` | `str` | required | VTherm service name (e.g. `"set_hvac_mode"`). |
| `action_data` | `dict \| None` | `None` | Service call data. |
| `blocking` | `bool` | `False` | Wait for service completion before returning. |
| `context` | `Context \| None` | `None` | HA context to propagate. |
| `return_response` | `bool` | `False` | Return the service response value. |

## Wait for the action to complete

```python
await plugin.call_linked_vtherm_action(
    "set_hvac_mode",
    action_data={"hvac_mode": "off"},
    blocking=True,
)
```

## Get a response value

```python
result = await plugin.call_linked_vtherm_action(
    "get_thermostat_info",
    return_response=True,
)
```

## Error handling

If no thermostat is linked, the method raises `RuntimeError`:

```python
plugin = PluginClimate(hass)
# Calling without link_to_vtherm raises RuntimeError
await plugin.call_linked_vtherm_action("set_hvac_mode", ...)
# → RuntimeError: No VTherm linked
```

Always call `link_to_vtherm(vtherm)` before forwarding actions.

## React to an event and send an action

A common pattern is to react to an event and immediately forward an action:

```python
class EcoOnSafetyPlugin(PluginClimate):
    def handle_safety_event(self, event: Event) -> None:
        data = self.get_event_data(EventType.SAFETY_EVENT)
        if data.get("safety_state"):
            # Safety triggered — schedule async action
            self._hass.async_create_task(
                self.call_linked_vtherm_action(
                    "set_preset_mode",
                    action_data={"preset_mode": "eco"},
                )
            )
```

Note: `handle_*` methods are synchronous. Use `hass.async_create_task(...)` to schedule async actions from within them.
