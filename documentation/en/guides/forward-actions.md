# Guide: Forward actions to VTherm

## Goal

Send a command to one linked VTherm thermostat from your integration.

## How it works

`PluginClimate.call_linked_vtherm_action(...)` wraps `hass.services.async_call(...)` and automatically targets the linked thermostat entity.
You do not need to build `target={"entity_id": ...}` yourself.

## Basic usage

```python
await plugin.call_linked_vtherm_action(
    "set_hvac_mode",
    action_data={"hvac_mode": "heat"},
)

await plugin.call_linked_vtherm_action(
    "set_target_temperature",
    action_data={"temperature": 19.5},
)

await plugin.call_linked_vtherm_action(
    "set_preset_mode",
    action_data={"preset_mode": "eco"},
)
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `action_name` | `str` | required | VTherm service name |
| `action_data` | `dict | None` | `None` | Service data |
| `blocking` | `bool` | `False` | Wait for service completion |
| `context` | `Context | None` | `None` | HA context to propagate |
| `return_response` | `bool` | `False` | Return the service response |

## Error handling

If no thermostat is linked, the method raises `RuntimeError`:

```python
plugin = PluginClimate(hass)
await plugin.call_linked_vtherm_action("set_hvac_mode")
# RuntimeError: No linked VTherm configured
```

Always call `link_to_vtherm(...)` first.

## Real-world example: climate replication

`vtherm_climate_replication` uses `PluginClimate` mainly as a linking and forwarding helper.
It listens to a physical climate entity, then mirrors selected changes to a target VTherm climate.

```python
from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    PRESET_NONE,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
    SERVICE_SET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.helpers.event import async_track_state_change_event

from vtherm_api import PluginClimate


class ClimateReplication:
    def __init__(self, hass, physical_entity_id: str, target_entity_id: str) -> None:
        self._hass = hass
        self._physical_entity_id = physical_entity_id
        self._target_entity_id = target_entity_id
        self._plugin = PluginClimate(hass)

    async def async_setup(self) -> None:
        self._link_to_target_vtherm()
        async_track_state_change_event(
            self._hass,
            self._physical_entity_id,
            self._handle_change,
        )

    def _link_to_target_vtherm(self) -> bool:
        component = self._hass.data.get("climate")
        if component is None:
            return False

        vtherm = component.get_entity(self._target_entity_id)
        if vtherm is None:
            return False

        self._plugin.link_to_vtherm(vtherm)
        return True

    async def _handle_change(self, event) -> None:
        new_state = event.data.get("new_state")
        if new_state is None or not self._link_to_target_vtherm():
            return

        await self._plugin.call_linked_vtherm_action(
            SERVICE_SET_HVAC_MODE,
            {ATTR_HVAC_MODE: new_state.attributes.get(ATTR_HVAC_MODE, new_state.state)},
        )

        temperature = new_state.attributes.get(ATTR_TEMPERATURE)
        if temperature is not None:
            await self._plugin.call_linked_vtherm_action(
                SERVICE_SET_TEMPERATURE,
                {ATTR_TEMPERATURE: temperature},
            )

        linked_vtherm = self._plugin.linked_vtherm
        if linked_vtherm and (
            linked_vtherm.supported_features & ClimateEntityFeature.PRESET_MODE
        ):
            await self._plugin.call_linked_vtherm_action(
                SERVICE_SET_PRESET_MODE,
                {ATTR_PRESET_MODE: new_state.attributes.get(ATTR_PRESET_MODE) or PRESET_NONE},
            )
```

This pattern shows that:

- `PluginClimate` can be useful even if you do not override any event handler
- direct linking through the climate component is often simpler than `VThermAPI.link_to_vtherm(...)`
- relinking on demand is a valid strategy if HA recreates the target entity

## React to a VTherm event and send an action

If you subclass `PluginClimate`, you can also react to VTherm events and forward commands back to the same thermostat:

```python
from homeassistant.core import Event

from vtherm_api import PluginClimate
from vtherm_api.const import EventType


class EcoOnSafetyPlugin(PluginClimate):
    def handle_safety_event(self, event: Event) -> None:
        data = self.get_event_data(EventType.SAFETY_EVENT)
        if data.get("safety_state"):
            self._hass.async_create_task(
                self.call_linked_vtherm_action(
                    "set_preset_mode",
                    action_data={"preset_mode": "eco"},
                )
            )
```

`handle_*` methods are synchronous, so async service calls should be scheduled with `hass.async_create_task(...)`.
