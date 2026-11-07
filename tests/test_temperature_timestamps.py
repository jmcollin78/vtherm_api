"""Optional freshness-clock capability and compatibility with older runtimes."""

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import get_type_hints

from src import vtherm_api
from src.vtherm_api.interfaces import (
    InterfaceTemperatureTimestampRuntime,
    InterfaceThermostatRuntime,
)


def _legacy_runtime():
    """Model the complete original surface, without assuming timestamp support."""
    return SimpleNamespace(
        **{
            name: (lambda *args, **kwargs: None) if callable(getattr(InterfaceThermostatRuntime, name, None)) else None
            for name in InterfaceThermostatRuntime.__protocol_attrs__
        }
    )


def test_legacy_runtime_does_not_require_timestamps():
    runtime = _legacy_runtime()
    assert isinstance(runtime, InterfaceThermostatRuntime)
    assert not isinstance(runtime, InterfaceTemperatureTimestampRuntime)


def test_capability_requires_both_clocks_and_accepts_unknown_values():
    runtime = _legacy_runtime()
    runtime.last_temperature_measure = None
    assert not isinstance(runtime, InterfaceTemperatureTimestampRuntime)
    runtime.last_ext_temperature_measure = None
    assert isinstance(runtime, InterfaceTemperatureTimestampRuntime)
    assert isinstance(runtime, InterfaceThermostatRuntime)


def test_timestamp_capability_does_not_normalize_or_invent_measurements():
    runtime = _legacy_runtime()
    measured = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)
    runtime.last_temperature_measure = measured
    runtime.last_ext_temperature_measure = measured
    assert isinstance(runtime, InterfaceTemperatureTimestampRuntime)
    assert runtime.last_temperature_measure is measured
    # Freshness clocks may exist even before a temperature is available.
    assert runtime.current_temperature is None


def test_public_export_and_property_types():
    assert vtherm_api.InterfaceTemperatureTimestampRuntime is InterfaceTemperatureTimestampRuntime
    assert "InterfaceTemperatureTimestampRuntime" in vtherm_api.__all__
    for name in ("last_temperature_measure", "last_ext_temperature_measure"):
        prop = getattr(InterfaceTemperatureTimestampRuntime, name)
        assert isinstance(prop, property)
        assert get_type_hints(prop.fget)["return"] == datetime | None
