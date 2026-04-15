# Guide: Create a FeatureManager

## Goal

Extend VTherm thermostat behavior with a custom feature that can be enabled/disabled dynamically, respond to HA events, and expose detection state back to the thermostat.

## Concepts

- **`InterfaceFeatureManager`**: a protocol (contract) that your manager must implement.
- **`api.register_manager(manager)`**: registers the manager to all VTherm entities found in HA.
- The thermostat calls `manager.register_manager(...)` internally — your manager just needs to be registered once via the API.

## Step 1: Implement the manager

```python
from typing import Any

from homeassistant.core import CALLBACK_TYPE, HomeAssistant

from vtherm_api import VThermAPI
from vtherm_api.interfaces import InterfaceFeatureManager


class MyFeatureManager:
    """Custom feature manager that detects an external condition."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._is_configured = False
        self._is_detected = False
        self._listeners: list[CALLBACK_TYPE] = []

    def post_init(self, entry_infos: dict[str, Any]) -> None:
        """
        Called after creation with the merged config entry data.
        Use this to read configuration keys.
        """
        self._is_configured = entry_infos.get("my_feature_enabled", False)

    async def start_listening(self, force: bool = False) -> None:
        """Subscribe to HA events or state changes needed by this manager."""
        # Example: subscribe to a sensor state change
        # cancel = self._hass.bus.async_listen("state_changed", self._on_state_changed)
        # self._listeners.append(cancel)

    def stop_listening(self) -> bool:
        """Unsubscribe all listeners registered via add_listener."""
        for cancel in list(self._listeners):
            cancel()
        self._listeners.clear()
        return True

    async def refresh_state(self) -> bool:
        """
        Refresh internal detection state.
        Return True if the state changed.
        """
        previous = self._is_detected
        # Example: check an external condition
        api = VThermAPI.get_vtherm_api(self._hass)
        self._is_detected = api is not None and self._is_configured
        return self._is_detected != previous

    def restore_state(self, old_state: Any) -> None:
        """Restore state from a previous HA state object (on restart)."""

    def add_listener(self, func: CALLBACK_TYPE) -> None:
        """Register a cleanup callback (called by VTherm on stop)."""
        self._listeners.append(func)

    @property
    def is_configured(self) -> bool:
        """Is the manager properly configured?"""
        return self._is_configured

    @property
    def is_detected(self) -> bool:
        """Is the manager's condition currently active?"""
        return self._is_detected

    @property
    def name(self) -> str:
        return "MyFeatureManager"

    @property
    def hass(self) -> HomeAssistant:
        return self._hass
```

## Step 2: Register the manager

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from vtherm_api import VThermAPI


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = VThermAPI.get_vtherm_api(hass)
    api.add_entry(entry)

    manager = MyFeatureManager(hass)
    manager.post_init(dict(entry.data))  # Pass config entry data
    await manager.refresh_state()        # Set initial state

    api.register_manager(manager)        # Forward to all VTherm entities
    return True
```

## Step 3: Unload

```python
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # VTherm calls stop_listening on its managed feature managers
    # You can also call it explicitly if you hold a reference
    api = VThermAPI.get_vtherm_api()
    if api is not None:
        api.remove_entry(entry)
    return True
```

## How VTherm uses the manager

When `api.register_manager(manager)` is called, the API:

1. Scans the Home Assistant `climate` component for all entities.
2. For each entity that implements `InterfaceThermostat` and has `device_info["model"] == "versatile_thermostat"`:
   - Calls `entity.register_manager(manager)`.

The thermostat then:
- Calls `manager.post_init(entry_infos)` with merged config.
- Calls `await manager.start_listening()` to activate subscriptions.
- Polls `manager.is_detected` to adjust behavior.
- Calls `manager.stop_listening()` on unload.

## Minimal thermostat test double

For unit tests, create a fake thermostat that satisfies `InterfaceThermostat`:

```python
from vtherm_api.const import DOMAIN
from vtherm_api.interfaces import InterfaceFeatureManager, InterfaceThermostat


class FakeVTherm:
    def __init__(self) -> None:
        self.managers: list[InterfaceFeatureManager] = []

    @property
    def name(self) -> str:
        return "FakeVTherm"

    @property
    def unique_id(self) -> str:
        return "fake-vtherm-001"

    @property
    def device_info(self) -> dict:
        return {"model": DOMAIN}

    def register_manager(self, manager: InterfaceFeatureManager) -> None:
        self.managers.append(manager)
```
