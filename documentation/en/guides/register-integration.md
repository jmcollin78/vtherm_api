# Guide: Register your integration with VThermAPI

## Goal

Make your custom integration aware of the VTherm runtime by creating or retrieving the shared `VThermAPI` singleton.

## Why this is needed

`VThermAPI` is the shared singleton that:

- holds a reference to the `HomeAssistant` object
- exposes `api.now` as a timezone-aware clock
- manages the proportional algorithm registry
- exposes `register_manager(...)` for feature manager registration

Unlike older drafts of this documentation, the current API does not expose `add_entry(...)` or `remove_entry(...)`.

## Step 1: Setup

In your integration's `__init__.py` or equivalent setup module:

```python
from vtherm_api import VThermAPI


async def async_setup_entry(hass, entry) -> bool:
    api = VThermAPI.get_vtherm_api(hass)
    if api is None:
        return False

    return True
```

## Step 2: Use the singleton for the API feature you need

### Register a proportional algorithm

This is the pattern used by `vtherm_smartpi`:

```python
from vtherm_api import VThermAPI

from .factory import SmartPIHandlerFactory


async def async_setup_entry(hass, entry) -> bool:
    api = VThermAPI.get_vtherm_api(hass)
    if api is None:
        return False

    factory = SmartPIHandlerFactory()
    if api.get_prop_algorithm(factory.name) is None:
        api.register_prop_algorithm(factory)

    return True
```

### Register a feature manager

```python
from vtherm_api import VThermAPI


async def async_setup_entry(hass, entry) -> bool:
    api = VThermAPI.get_vtherm_api(hass)
    if api is None:
        return False

    manager = MyFeatureManager(hass)
    manager.post_init(dict(entry.data))
    await manager.refresh_state()
    api.register_manager(manager)
    return True
```

## Step 3: Unload

There is no explicit unregister call for the singleton itself.
On unload, you typically only undo what your own integration registered:

```python
async def async_unload_entry(hass, entry) -> bool:
    api = VThermAPI.get_vtherm_api()
    if api is not None:
        api.unregister_prop_algorithm("my_algorithm")
    return True
```

## Notes

- Calling `get_vtherm_api(hass)` multiple times is safe.
- The singleton lives in `hass.data["versatile_thermostat"]["vtherm_api"]`.
- If VTherm is not loaded yet when your integration sets up, `get_vtherm_api(hass)` still creates the singleton.
