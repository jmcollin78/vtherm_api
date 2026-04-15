# Guide: Register a proportional algorithm

## Goal

Replace or extend VTherm's proportional heating control algorithm with a custom implementation.

## Concepts

- **`InterfacePropAlgorithmFactory`**: a named factory that VTherm uses to create algorithm handlers.
- **`InterfacePropAlgorithmHandler`**: the lifecycle object bound to one thermostat instance, called by VTherm during each control cycle.
- **`InterfaceThermostatRuntime`**: the thermostat view exposed to the handler, providing read access to temperatures, HVAC state, and the cycle scheduler.

## Step 1: Implement the handler

```python
from datetime import datetime
from typing import Any

from vtherm_api import InterfacePropAlgorithmHandler, InterfaceThermostatRuntime
from vtherm_api.interfaces import InterfaceCycleScheduler


class MyAlgorithmHandler:
    """Custom proportional algorithm handler."""

    def __init__(self, thermostat: InterfaceThermostatRuntime) -> None:
        self._thermostat = thermostat
        self._scheduler: InterfaceCycleScheduler | None = None

    def init_algorithm(self) -> None:
        """Set up the algorithm object on the thermostat."""
        # Assign whatever object VTherm expects as prop_algorithm
        self._thermostat.prop_algorithm = self

    async def async_added_to_hass(self) -> None:
        """Called when the thermostat entity is added to HA."""

    async def async_startup(self) -> None:
        """Called after thermostat initialization — safe to read config here."""

    def remove(self) -> None:
        """Release any resources (listeners, timers, etc.)."""

    async def control_heating(
        self,
        timestamp: datetime | None = None,
        force: bool = False,
    ) -> None:
        """
        Main control loop — called every cycle.

        Use self._thermostat to read temperatures and state.
        Use self._scheduler to start/stop cycles.
        """
        current = self._thermostat.current_temperature
        target = self._thermostat.target_temperature

        if current is None or target is None:
            return

        # Simple bang-bang example:
        if current < target - 0.5:
            on_percent = 1.0
        elif current > target + 0.5:
            on_percent = 0.0
        else:
            on_percent = (target - current + 0.5)  # proportional

        if self._scheduler is not None:
            await self._scheduler.start_cycle(
                hvac_mode=self._thermostat.vtherm_hvac_mode,
                on_percent=max(0.0, min(1.0, on_percent)),
            )

    async def on_state_changed(self) -> None:
        """React to thermostat state change (preset, HVAC mode, etc.)."""

    def on_scheduler_ready(self, scheduler: InterfaceCycleScheduler) -> None:
        """Receive the cycle scheduler once it is initialized."""
        self._scheduler = scheduler

    def should_publish_intermediate(self) -> bool:
        """Return True to allow VTherm to publish intermediate states."""
        return True
```

## Step 2: Implement the factory

```python
from vtherm_api import InterfacePropAlgorithmFactory, InterfaceThermostatRuntime


class MyAlgorithmFactory:
    """Factory registered with VThermAPI."""

    @property
    def name(self) -> str:
        return "my_algorithm"  # Unique identifier — used in config

    def create(self, thermostat: InterfaceThermostatRuntime) -> MyAlgorithmHandler:
        return MyAlgorithmHandler(thermostat)
```

## Step 3: Register the factory

Register the factory when your integration sets up:

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from vtherm_api import VThermAPI


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = VThermAPI.get_vtherm_api(hass)
    api.register_prop_algorithm(MyAlgorithmFactory())
    return True
```

## Step 4: Unregister on unload

```python
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = VThermAPI.get_vtherm_api()
    if api is not None:
        api.unregister_prop_algorithm("my_algorithm")
        api.remove_entry(entry)
    return True
```

## List registered algorithms

```python
api = VThermAPI.get_vtherm_api(hass)
names = api.list_prop_algorithms()
# → ["my_algorithm", "smart_pi", ...]
```

## Reading thermostat state

Inside `control_heating`, use `InterfaceThermostatRuntime` properties:

```python
async def control_heating(self, timestamp=None, force: bool = False) -> None:
    t_current = self._thermostat.current_temperature
    t_outdoor = self._thermostat.current_outdoor_temperature
    t_target  = self._thermostat.target_temperature
    slope     = self._thermostat.last_temperature_slope
    mode      = self._thermostat.vtherm_hvac_mode
    cycle_min = self._thermostat.cycle_min
    active    = self._thermostat.is_device_active
```

See [InterfaceThermostatRuntime](../api-reference.md#interfacethermostatruntime) for the full list of available properties.
