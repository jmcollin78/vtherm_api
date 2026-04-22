# Architecture

## Component overview

```text
Home Assistant runtime
    |
    +-- VThermAPI singleton in hass.data
    |     - access to hass
    |     - access to now
    |     - proportional algorithm registry
    |     - manager registration helper
    |
    +-- Versatile Thermostat climate entities
    |     - emit VTherm events on the HA bus
    |     - expose runtime interfaces to algorithm handlers
    |
    +-- PluginClimate helpers
          - subscribe to VTherm events for one linked thermostat
          - cache the latest payload per event type
          - forward HA service calls back to the linked thermostat
```

## Event flow

```text
VTherm entity
    |
    | emits versatile_thermostat_temperature_event
    v
HA Event Bus
    |
    v
PluginClimate listener
    |
    +-- ignore the event if entity_id does not match the linked VTherm
    +-- store the payload in the local event cache
    +-- dispatch to handle_temperature_event(event)
    |
    +-- optional:
        call_linked_vtherm_action(...)
            |
            v
        hass.services.async_call(
            domain="versatile_thermostat",
            service="set_target_temperature",
            target={"entity_id": linked_entity_id},
        )
```

## VThermAPI lifecycle

`VThermAPI` is stored in `hass.data[DOMAIN][VTHERM_API_NAME]`.

```text
async_setup_entry
    |
    v
VThermAPI.get_vtherm_api(hass)
    |
    +-- existing instance -> return it
    +-- no instance yet   -> create it, store it, return it

async_unload_entry
    |
    v
VThermAPI.get_vtherm_api()
    |
    +-- reuse the existing singleton if needed
```

## Proportional algorithm lifecycle

```text
Integration setup
    |
    v
api.register_prop_algorithm(factory)
    |
    v
VTherm creates thermostat runtime
    |
    v
factory.create(thermostat)
    |
    v
handler.init_algorithm()
handler.async_added_to_hass()
handler.async_startup()
    |
    +-- on every control iteration:
    |   handler.control_heating(timestamp, force)
    |
    +-- when thermostat state changes:
    |   handler.on_state_changed(changed)
    |
    +-- when scheduler becomes available:
    |   handler.on_scheduler_ready(scheduler)
    |
    +-- on unload:
        handler.remove()
```

## Real-world mappings

- `vtherm_smartpi` uses the proportional algorithm lifecycle extensively.
- `vtherm_climate_replication` mostly uses the `PluginClimate` service-forwarding side and links directly to a target VTherm entity from the climate component.

## Protocol-based design

All contracts between the API and VTherm are defined as runtime-checkable `Protocol` classes.
This means plugins do not need to import VTherm internals directly and can rely on duck typing.
