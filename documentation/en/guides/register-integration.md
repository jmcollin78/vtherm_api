# Guide: Register your integration with VThermAPI

## Goal

Make your custom integration aware of the VTherm runtime by registering your config entry with `VThermAPI`.

## Why this is needed

`VThermAPI` is the shared singleton that:
- holds a reference to the `HomeAssistant` object
- exposes `api.now` (timezone-aware datetime)
- manages the proportional algorithm and feature manager registries

Your integration should register itself on setup and deregister on unload.

## Step 1: Setup

In your integration's `__init__.py` (or wherever you handle `async_setup_entry`):

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from vtherm_api import VThermAPI


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Create or retrieve the singleton, then register this entry
    api = VThermAPI.get_vtherm_api(hass)
    api.add_entry(entry)

    # api.hass is now available
    # api.now returns a timezone-aware datetime

    return True
```

## Step 2: Unload

```python
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = VThermAPI.get_vtherm_api()  # No hass needed — retrieves existing instance
    if api is not None:
        api.remove_entry(entry)
    return True
```

## Notes

- Calling `get_vtherm_api(hass)` multiple times is safe — it always returns the same instance.
- The singleton lives in `hass.data["versatile_thermostat"]["vtherm_api"]`.
- If VTherm is not loaded yet when your integration sets up, `get_vtherm_api(hass)` still works — it creates the singleton. VTherm will discover it when it loads.
