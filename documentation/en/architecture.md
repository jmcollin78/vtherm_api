# Architecture

## Component overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Home Assistant runtime                     │
│                                                                 │
│  ┌─────────────┐    ┌──────────────────────────────────────┐   │
│  │ ConfigEntry │───▶│  VThermAPI (singleton in hass.data)  │   │
│  └─────────────┘    │                                      │   │
│                     │  - entry registry                    │   │
│                     │  - prop algorithm registry           │   │
│                     │  - feature manager registry          │   │
│                     └──────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────┐     ┌───────────────────────────┐    │
│  │  Versatile Thermostat │────▶│   HA Event Bus            │    │
│  │  entity (VTherm)      │     │                           │    │
│  └──────────────────────┘     └────────────┬──────────────┘    │
│                                            │                   │
│                                   ┌────────▼────────┐          │
│                                   │  PluginClimate  │          │
│                                   │                 │          │
│                                   │  - event cache  │          │
│                                   │  - handle_*()   │          │
│                                   └────────┬────────┘          │
│                                            │                   │
│                              ┌─────────────▼──────────────┐    │
│                              │   HA Service Registry      │    │
│                              │   domain: versatile_thermo │    │
│                              └─────────────┬──────────────┘    │
│                                            │                   │
│                              ┌─────────────▼──────────────┐    │
│                              │  Versatile Thermostat      │    │
│                              │  entity (action executed)  │    │
│                              └────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Event flow

```
VTherm entity
    │
    │  emits: versatile_thermostat_temperature_event
    ▼
HA Event Bus
    │
    │  dispatched to all registered listeners
    ▼
PluginClimate listener
    │
    ├── check entity_id matches linked thermostat → ignore if not
    ├── store payload in event cache
    ├── call handle_temperature_event(event)
    │
    └── (optional) call_linked_vtherm_action(...)
            │
            ▼
        hass.services.async_call(
            domain="versatile_thermostat",
            service="set_target_temperature",
            target={"entity_id": linked_entity_id},
            ...
        )
```

## Singleton lifecycle

`VThermAPI` is stored in `hass.data[DOMAIN][VTHERM_API_NAME]`.

```
async_setup_entry called
    │
    ▼
VThermAPI.get_vtherm_api(hass)
    │
    ├── instance already in hass.data? → return it
    └── not found → create new instance, store in hass.data, return it

async_unload_entry called
    │
    ▼
VThermAPI.get_vtherm_api()   ← no hass argument → returns existing
    │
    └── api.remove_entry(entry)
```

## Plugin algorithm lifecycle

```
Integration setup
    │
    ▼
api.register_prop_algorithm(factory)
    │                                   ← factory stored in registry by name
    ▼
VTherm creates thermostat entity
    │
    ▼
VTherm calls factory.create(thermostat)
    │
    ▼
handler.init_algorithm()
handler.async_added_to_hass()
handler.async_startup()
    │
    │  (on each cycle)
    ▼
handler.control_heating(timestamp, force)
    │
    │  (on state change)
    ▼
handler.on_state_changed()
    │
    │  (on unload)
    ▼
handler.remove()
```

## Protocol-based design

All contracts between the API and VTherm (and between plugins and VTherm) are defined as `@runtime_checkable` `Protocol` classes. This means:

- Plugins do **not** need to import VTherm source code.
- Type checking works with duck-typing: any class implementing the required attributes and methods satisfies the protocol.
- Protocols can be verified at runtime with `isinstance(obj, InterfaceXxx)`.

See [Interfaces](api-reference.md#interfaces) for the full list.
