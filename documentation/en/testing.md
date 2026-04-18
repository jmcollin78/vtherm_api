# Testing

## Overview

`vtherm_api` is designed to be testable. Key features that help:

- `VThermAPI.reset_vtherm_api()` resets the singleton between tests.
- `api._set_now(datetime)` overrides the clock.
- All interfaces are Protocols — easy to implement as test doubles.
- `PluginClimate.handle_vtherm_event(event)` can be called directly without a real HA event bus.

## Setup and teardown

Always reset the singleton after each test to avoid state leakage:

```python
import pytest
from vtherm_api import VThermAPI


@pytest.fixture(autouse=True)
def reset_api():
    yield
    VThermAPI.reset_vtherm_api()
```

## Mock hass

A minimal `hass` mock for most tests:

```python
from unittest.mock import AsyncMock, MagicMock

hass = MagicMock()
hass.services.async_call = AsyncMock(return_value=None)
hass.bus.async_listen = MagicMock(return_value=lambda: None)  # Returns cancel function
```

## Testing VThermAPI

```python
from unittest.mock import MagicMock
from vtherm_api import VThermAPI


def test_singleton_is_shared():
    hass = MagicMock()
    api1 = VThermAPI.get_vtherm_api(hass)
    api2 = VThermAPI.get_vtherm_api(hass)
    assert api1 is api2


def test_without_hass_returns_none_if_not_created():
    assert VThermAPI.get_vtherm_api() is None


def test_prop_algorithm_registry():
    hass = MagicMock()
    api = VThermAPI.get_vtherm_api(hass)

    factory = MagicMock()
    factory.name = "test_algo"

    api.register_prop_algorithm(factory)
    assert "test_algo" in api.list_prop_algorithms()
    assert api.get_prop_algorithm("test_algo") is factory

    api.unregister_prop_algorithm("test_algo")
    assert api.get_prop_algorithm("test_algo") is None
```

## Testing PluginClimate event handling

```python
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from homeassistant.core import Event

from vtherm_api import PluginClimate
from vtherm_api.const import EventType


@pytest.mark.asyncio
async def test_temperature_event_is_cached():
    hass = MagicMock()
    hass.bus.async_listen = MagicMock(return_value=lambda: None)

    plugin = PluginClimate(hass)
    plugin.link_to_vtherm(SimpleNamespace(entity_id="climate.salon"))

    # Build a fake event
    event = Event(
        EventType.TEMPERATURE_EVENT.value,
        data={
            "entity_id": "climate.salon",
            "current_temperature": 20.5,
            "target_temperature": 21.0,
        },
    )
    plugin.handle_vtherm_event(event)

    assert plugin.last_event_type == EventType.TEMPERATURE_EVENT
    data = plugin.get_event_data(EventType.TEMPERATURE_EVENT)
    assert data["current_temperature"] == 20.5


def test_event_from_wrong_entity_is_ignored():
    hass = MagicMock()
    hass.bus.async_listen = MagicMock(return_value=lambda: None)

    plugin = PluginClimate(hass)
    plugin.link_to_vtherm(SimpleNamespace(entity_id="climate.salon"))

    event = Event(
        EventType.TEMPERATURE_EVENT.value,
        data={"entity_id": "climate.bedroom", "current_temperature": 19.0},
    )
    plugin.handle_vtherm_event(event)

    assert plugin.last_event_type is None
```

## Testing action forwarding

```python
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from vtherm_api import PluginClimate


@pytest.mark.asyncio
async def test_call_linked_vtherm_action():
    hass = MagicMock()
    hass.bus.async_listen = MagicMock(return_value=lambda: None)
    hass.services.async_call = AsyncMock(return_value="ok")

    plugin = PluginClimate(hass)
    plugin.link_to_vtherm(SimpleNamespace(entity_id="climate.salon"))

    result = await plugin.call_linked_vtherm_action(
        "set_hvac_mode",
        action_data={"hvac_mode": "heat"},
        blocking=True,
    )

    assert result == "ok"
    hass.services.async_call.assert_called_once_with(
        "versatile_thermostat",
        "set_hvac_mode",
        {"hvac_mode": "heat"},
        True,
        None,
        {"entity_id": "climate.salon"},
        False,
    )


@pytest.mark.asyncio
async def test_call_action_without_link_raises():
    hass = MagicMock()
    plugin = PluginClimate(hass)

    with pytest.raises(RuntimeError):
        await plugin.call_linked_vtherm_action("set_hvac_mode")
```

## Overriding the clock

```python
from datetime import datetime, timezone


def test_with_fixed_time():
    hass = MagicMock()
    api = VThermAPI.get_vtherm_api(hass)

    fixed = datetime(2025, 1, 15, 10, 30, tzinfo=timezone.utc)
    api._set_now(fixed)

    assert api.now == fixed
```

## Testing FeatureManager registration

```python
from vtherm_api import VThermAPI
from vtherm_api.const import DOMAIN


class FakeVTherm:
    def __init__(self):
        self.managers = []

    @property
    def name(self): return "FakeVTherm"

    @property
    def unique_id(self): return "fake-001"

    @property
    def device_info(self): return {"model": DOMAIN}

    def register_manager(self, manager): self.managers.append(manager)


def test_register_manager_reaches_vtherm(hass_with_climate):
    """
    hass_with_climate is a fixture that injects a FakeVTherm entity
    into the climate component.
    """
    hass, fake_vtherm = hass_with_climate

    api = VThermAPI.get_vtherm_api(hass)
    manager = MagicMock()

    api.register_manager(manager)

    assert manager in fake_vtherm.managers
```

## Tips

- Use `link_to_vtherm(SimpleNamespace(entity_id="..."))` to avoid needing a real HA entity.
- For async tests, use `pytest-asyncio` with `@pytest.mark.asyncio`.
- Mock `hass.bus.async_listen` to return a cancel function (`lambda: None`) so `remove_listeners()` works without errors.
- Always reset the singleton in teardown with `VThermAPI.reset_vtherm_api()`.
