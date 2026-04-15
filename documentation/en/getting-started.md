# Getting started

## Installation

### In a Home Assistant custom integration

Add `vtherm_api` as a dependency in your integration's `manifest.json`:

```json
{
  "domain": "my_vtherm_plugin",
  "name": "My VTherm Plugin",
  "requirements": ["vtherm_api>=0.2.0"],
  "dependencies": ["versatile_thermostat"]
}
```

### For local development

Clone the repository, then install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

Run the test suite to verify the setup:

```bash
pytest
```

## Minimum requirements

- Python 3.14+
- Home Assistant with Versatile Thermostat installed and configured
- At least one VTherm climate entity registered in Home Assistant

## Public imports

All main classes and interfaces are exported from the package root:

```python
from vtherm_api import (
    InterfaceCycleScheduler,
    InterfaceFeatureManager,
    InterfacePropAlgorithmFactory,
    InterfacePropAlgorithmHandler,
    InterfaceThermostat,
    InterfaceThermostatRuntime,
    PluginClimate,
    VThermAPI,
    __version__,
)
from vtherm_api.const import DOMAIN, EventType
```

## First integration: register with VThermAPI

The minimal integration registers its config entry with the API on setup, and removes it on unload:

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from vtherm_api import VThermAPI


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = VThermAPI.get_vtherm_api(hass)
    api.add_entry(entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = VThermAPI.get_vtherm_api()
    if api is not None:
        api.remove_entry(entry)
    return True
```

## Next steps

- [Listen to thermostat events](guides/listen-to-events.md) — subscribe to VTherm events with `PluginClimate`
- [Register a proportional algorithm](guides/proportional-algorithm.md) — plug in a custom control algorithm
- [Create a FeatureManager](guides/feature-manager.md) — extend thermostat behavior
- [Forward actions to VTherm](guides/forward-actions.md) — send commands back to a thermostat
