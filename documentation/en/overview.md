# Overview

## What is vtherm_api?

`vtherm_api` is a Python package for Home Assistant that lets external integrations interact with **Versatile Thermostat** (VTherm) entities programmatically.

It is **not** a REST or HTTP API. It is a Python library designed to be imported inside Home Assistant integration code.

## What problems does it solve?

When you build a custom Home Assistant integration around Versatile Thermostat, you typically need to:

1. Keep a stable reference to the VTherm runtime across the integration lifecycle.
2. Track one or more specific VTherm climate entities.
3. Listen only to events emitted by those entities (not all thermostats).
4. Forward actions such as HVAC mode or target temperature changes back to the linked thermostat.
5. Optionally replace or extend VTherm's proportional control algorithm.
6. Optionally add a feature manager that extends thermostat behavior.

`vtherm_api` provides all of these as reusable building blocks.

## Main building blocks

| Component | Purpose |
|---|---|
| `VThermAPI` | Singleton attached to `hass.data`. Exposes `hass` and `now`, manages the proportional algorithm registry, and registers feature managers. |
| `PluginClimate` | Event listener + service forwarder bound to one linked VTherm entity. |
| `InterfacePropAlgorithmFactory` / `InterfacePropAlgorithmHandler` | Protocols for registering a custom proportional algorithm. |
| `InterfaceFeatureManager` | Protocol for a feature manager that extends thermostat behavior. |
| `InterfaceThermostat` / `InterfaceThermostatRuntime` | Contracts describing what VTherm exposes to plugins. |

## Package version

```python
from vtherm_api import __version__
print(__version__)  # e.g. "0.2.0"
```

## Requirements

- Python 3.14+
- Home Assistant runtime objects (`HomeAssistant`, `ConfigEntry`, `Event`, etc.)
- A Versatile Thermostat entity already registered in Home Assistant
