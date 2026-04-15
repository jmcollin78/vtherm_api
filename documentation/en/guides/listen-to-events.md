# Guide: Listen to thermostat events

## Goal

Subscribe to events emitted by a specific VTherm entity and react to them inside your integration.

## Step 1: Subclass PluginClimate

Create a subclass and override only the handlers you need. All handlers are optional.

```python
from typing import Any

from homeassistant.core import Event, HomeAssistant

from vtherm_api import PluginClimate
from vtherm_api.const import EventType


class MyPluginClimate(PluginClimate):
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)
        self.last_temperature: float | None = None
        self.last_preset: str | None = None

    def handle_temperature_event(self, event: Event) -> None:
        # Get the cached payload for this event type
        data = self.get_event_data(EventType.TEMPERATURE_EVENT)
        self.last_temperature = data.get("current_temperature")

    def handle_preset_event(self, event: Event) -> None:
        data = self.get_event_data(EventType.PRESET_EVENT)
        self.last_preset = data.get("preset_mode")

    def handle_hvac_mode_event(self, event: Event) -> None:
        data = self.get_event_data(EventType.HVAC_MODE_EVENT)
        # React to mode change...
```

## Step 2: Link to a thermostat

You need an object that exposes `entity_id`. In production this is your VTherm entity. In tests you can use a `SimpleNamespace`.

```python
from types import SimpleNamespace

plugin = MyPluginClimate(hass)
plugin.link_to_vtherm(SimpleNamespace(entity_id="climate.living_room"))
```

From this point on, all events emitted by `climate.living_room` will be routed to your handlers.

## Step 3: Read cached event data

You can read the latest payload at any time without waiting for an event:

```python
temp_data = plugin.get_event_data(EventType.TEMPERATURE_EVENT)
current_temp = temp_data.get("current_temperature")  # None if no event yet
```

You can also check what the last event type was:

```python
last = plugin.last_event_type  # EventType.TEMPERATURE_EVENT or None
```

## Step 4: Clean up on unload

When your integration unloads, remove the event listeners:

```python
async def async_unload_entry(hass, entry):
    plugin.remove_listeners()
    return True
```

## Full example

```python
from types import SimpleNamespace

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant

from vtherm_api import PluginClimate
from vtherm_api.const import EventType


class RoomMonitor(PluginClimate):
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(hass)
        self.history: list[float] = []

    def handle_temperature_event(self, event: Event) -> None:
        data = self.get_event_data(EventType.TEMPERATURE_EVENT)
        t = data.get("current_temperature")
        if t is not None:
            self.history.append(t)

    def handle_safety_event(self, event: Event) -> None:
        data = self.get_event_data(EventType.SAFETY_EVENT)
        # Send alert, log, etc.


_monitor: RoomMonitor | None = None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    global _monitor
    _monitor = RoomMonitor(hass)
    _monitor.link_to_vtherm(SimpleNamespace(entity_id="climate.living_room"))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    global _monitor
    if _monitor is not None:
        _monitor.remove_listeners()
        _monitor = None
    return True
```

## See also

- [Events reference](../events.md) — all event types and their payloads
- [Forward actions to VTherm](forward-actions.md) — send commands back after an event
