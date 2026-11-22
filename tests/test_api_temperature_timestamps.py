"""Verify the public timestamp contract with a running VTherm entity."""

from homeassistant.core import HomeAssistant
from vtherm_api import InterfaceTemperatureTimestampRuntime

from .commons import create_thermostat
from .test_inhibition import switch_entry


async def test_vtherm_exposes_temperature_freshness_timestamps(
    hass: HomeAssistant,
    fake_temp_sensor,
    fake_ext_temp_sensor,
    fake_underlying_switch,
) -> None:
    thermostat = await create_thermostat(hass, switch_entry(), "climate.theoverswitchmockname")
    assert isinstance(thermostat, InterfaceTemperatureTimestampRuntime)

    fake_temp_sensor.set_native_value(21)
    fake_ext_temp_sensor.set_native_value(12)
    await hass.async_block_till_done()

    assert thermostat.current_temperature == 21
    assert thermostat.current_outdoor_temperature == 12
    for sensor, timestamp in (
        (fake_temp_sensor, thermostat.last_temperature_measure),
        (fake_ext_temp_sensor, thermostat.last_ext_temperature_measure),
    ):
        state = hass.states.get(sensor.entity_id)
        assert state is not None
        assert timestamp is not None
        assert timestamp.utcoffset() is not None
        assert timestamp == state.last_updated
