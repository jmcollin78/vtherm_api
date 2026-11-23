"""State-refresh and eligibility contracts exposed to feature managers."""

from collections.abc import Sequence
from dataclasses import dataclass
import inspect
from types import SimpleNamespace
from typing import get_type_hints
from unittest.mock import AsyncMock, Mock

import pytest

from src import vtherm_api
from src.vtherm_api.interfaces import InterfaceThermostatRuntime


@dataclass(frozen=True)
class FakeHvacMode:
    """Represent a core-specific mode without importing the VTherm core."""

    value: str

    def __str__(self) -> str:
        return self.value


@pytest.fixture
def fake_thermostat_runtime() -> SimpleNamespace:
    """Provide the runtime surface with observable state-refresh dispatch."""
    runtime = SimpleNamespace(
        **{
            name: Mock() if callable(getattr(InterfaceThermostatRuntime, name, None)) else None
            for name in InterfaceThermostatRuntime.__protocol_attrs__
        }
    )
    runtime.async_request_state_refresh = AsyncMock(return_value=None)
    runtime.has_valve_regulation = False
    runtime.vtherm_hvac_modes = [FakeHvacMode("off"), FakeHvacMode("heat")]
    return runtime


def test_refresh_request_is_a_public_async_contract() -> None:
    assert vtherm_api.InterfaceThermostatRuntime is InterfaceThermostatRuntime
    method = InterfaceThermostatRuntime.async_request_state_refresh
    assert inspect.iscoroutinefunction(method)
    assert list(inspect.signature(method).parameters) == ["self"]
    assert get_type_hints(method)["return"] is type(None)


@pytest.mark.asyncio
async def test_refresh_request_is_awaited_on_the_thermostat(
    fake_thermostat_runtime: SimpleNamespace,
) -> None:
    assert isinstance(fake_thermostat_runtime, InterfaceThermostatRuntime)
    thermostat: InterfaceThermostatRuntime = fake_thermostat_runtime

    request = thermostat.async_request_state_refresh()
    fake_thermostat_runtime.async_request_state_refresh.assert_called_once_with()
    fake_thermostat_runtime.async_request_state_refresh.assert_not_awaited()

    assert await request is None
    fake_thermostat_runtime.async_request_state_refresh.assert_awaited_once_with()


@pytest.mark.parametrize("has_valve_regulation", [False, True])
def test_valve_regulation_fact(
    fake_thermostat_runtime: SimpleNamespace,
    has_valve_regulation: bool,
) -> None:
    fake_thermostat_runtime.has_valve_regulation = has_valve_regulation
    assert isinstance(fake_thermostat_runtime, InterfaceThermostatRuntime)
    thermostat: InterfaceThermostatRuntime = fake_thermostat_runtime

    assert thermostat.has_valve_regulation is has_valve_regulation


@pytest.mark.parametrize(
    ("modes", "candidate", "accepted"),
    [
        (["off", "heat"], "fan_only", False),
        (["off", "heat", "fan_only", "dry"], "fan_only", True),
        (["off", "cool"], "dry", False),
        (["off", "cool", "dry"], "dry", True),
    ],
)
def test_accepted_hvac_modes_fact(
    fake_thermostat_runtime: SimpleNamespace,
    modes: list[str],
    candidate: str,
    accepted: bool,
) -> None:
    native_modes = [FakeHvacMode(mode) for mode in modes]
    fake_thermostat_runtime.vtherm_hvac_modes = native_modes
    assert isinstance(fake_thermostat_runtime, InterfaceThermostatRuntime)
    thermostat: InterfaceThermostatRuntime = fake_thermostat_runtime

    assert thermostat.vtherm_hvac_modes is native_modes
    assert [str(mode) for mode in thermostat.vtherm_hvac_modes] == modes
    assert (candidate in [str(mode) for mode in thermostat.vtherm_hvac_modes]) is accepted


@pytest.mark.parametrize(
    "member",
    ["async_request_state_refresh", "has_valve_regulation", "vtherm_hvac_modes"],
)
def test_runtime_check_requires_each_new_member(
    fake_thermostat_runtime: SimpleNamespace,
    member: str,
) -> None:
    assert isinstance(fake_thermostat_runtime, InterfaceThermostatRuntime)
    delattr(fake_thermostat_runtime, member)
    assert not isinstance(fake_thermostat_runtime, InterfaceThermostatRuntime)


def test_eligibility_properties_are_read_only_and_typed() -> None:
    for name, expected_type in (
        ("has_valve_regulation", bool),
        ("vtherm_hvac_modes", Sequence[object]),
    ):
        prop = getattr(InterfaceThermostatRuntime, name)
        assert isinstance(prop, property)
        assert prop.fget is not None
        assert prop.fset is None
        assert get_type_hints(prop.fget)["return"] == expected_type
