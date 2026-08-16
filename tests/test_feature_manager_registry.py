"""Tests for the feature manager registry exposed by VThermAPI."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from src.vtherm_api.const import DOMAIN
from src.vtherm_api.interfaces import (
    InterfaceFeatureManager,
    InterfaceFeatureManagerFactory,
    InterfaceThermostatRuntime,
)
from src.vtherm_api.vtherm_api import VThermAPI


class FakeFeatureManager(InterfaceFeatureManager):
    """Minimal feature manager used to validate the registry contract."""

    def post_init(self, entry_infos) -> None:
        """Initialize the manager."""
        del entry_infos

    async def start_listening(self, force: bool = False) -> None:
        """Subscribe to the required events."""
        del force

    def stop_listening(self) -> bool | None:
        """Unsubscribe the listeners."""
        return None

    async def refresh_state(self) -> bool:
        """Refresh the internal state."""
        return False

    def restore_state(self, old_state: Any) -> None:
        """Restore the manager state."""
        del old_state

    def add_listener(self, func) -> None:
        """Register a callback to remove on stop."""
        del func

    @property
    def is_configured(self) -> bool:
        """Return whether the manager is configured."""
        return True

    @property
    def is_detected(self) -> bool:
        """Return whether the manager detects its condition."""
        return False

    @property
    def name(self) -> str:
        """Return the manager name."""
        return "fake"

    @property
    def hass(self):
        """Return the Home Assistant instance."""
        return None


class FakeFeatureManagerFactory(InterfaceFeatureManagerFactory):
    """Minimal factory used to validate the registry contract."""

    def __init__(self, name: str, supported: bool = True) -> None:
        """Store the factory name and eligibility."""
        self._name = name
        self._supported = supported

    @property
    def name(self) -> str:
        """Return the factory name."""
        return self._name

    def supports(self, thermostat: InterfaceThermostatRuntime) -> bool:
        """Return whether the manager is eligible for the thermostat."""
        del thermostat
        return self._supported

    def create(
        self,
        thermostat: InterfaceThermostatRuntime,
    ) -> InterfaceFeatureManager:
        """Create a fake manager for the provided thermostat."""
        del thermostat
        return FakeFeatureManager()


def _build_hass() -> SimpleNamespace:
    """Create a minimal Home Assistant-like object for VThermAPI tests."""
    return SimpleNamespace(
        data={DOMAIN: {}},
        config=SimpleNamespace(time_zone="UTC"),
    )


def test_feature_manager_registry_lifecycle() -> None:
    """The registry should support register, get, list, and unregister."""
    VThermAPI.reset_vtherm_api()
    hass = _build_hass()
    api = VThermAPI.get_vtherm_api(hass)

    auto_fan_factory = FakeFeatureManagerFactory("auto_fan")
    other_factory = FakeFeatureManagerFactory("other")
    zeta_factory = FakeFeatureManagerFactory("zeta")

    api.register_feature_manager(other_factory)
    api.register_feature_manager(zeta_factory)
    api.register_feature_manager(auto_fan_factory)

    assert api.get_feature_manager("auto_fan") is auto_fan_factory
    assert api.list_feature_managers() == ["auto_fan", "other", "zeta"]
    assert api.get_feature_manager_factories() == [
        auto_fan_factory,
        other_factory,
        zeta_factory,
    ]

    api.unregister_feature_manager("other")

    assert api.get_feature_manager("other") is None
    assert api.list_feature_managers() == ["auto_fan", "zeta"]

    VThermAPI.reset_vtherm_api()


def test_register_feature_manager_replaces_existing_name() -> None:
    """Registering twice with the same name replaces the factory."""
    VThermAPI.reset_vtherm_api()
    hass = _build_hass()
    api = VThermAPI.get_vtherm_api(hass)

    first = FakeFeatureManagerFactory("auto_fan")
    second = FakeFeatureManagerFactory("auto_fan")

    api.register_feature_manager(first)
    api.register_feature_manager(second)

    assert api.get_feature_manager("auto_fan") is second
    assert api.list_feature_managers() == ["auto_fan"]

    VThermAPI.reset_vtherm_api()


def test_register_feature_manager_rejects_empty_names() -> None:
    """An empty factory name should be rejected."""
    VThermAPI.reset_vtherm_api()
    hass = _build_hass()
    api = VThermAPI.get_vtherm_api(hass)

    with pytest.raises(ValueError):
        api.register_feature_manager(FakeFeatureManagerFactory("   "))

    VThermAPI.reset_vtherm_api()


def test_feature_manager_factory_create_and_supports() -> None:
    """The factory should create managers and expose its scope decision."""
    VThermAPI.reset_vtherm_api()
    hass = _build_hass()
    api = VThermAPI.get_vtherm_api(hass)

    eligible = FakeFeatureManagerFactory("auto_fan", supported=True)
    ineligible = FakeFeatureManagerFactory("no_scope", supported=False)
    api.register_feature_manager(eligible)
    api.register_feature_manager(ineligible)

    runtime = SimpleNamespace()

    assert eligible.supports(runtime) is True
    assert ineligible.supports(runtime) is False

    manager = eligible.create(runtime)
    assert isinstance(manager, InterfaceFeatureManager)

    VThermAPI.reset_vtherm_api()


def test_reset_vtherm_api_recreates_an_empty_feature_manager_registry() -> None:
    """Resetting the API should drop the current registry content."""
    VThermAPI.reset_vtherm_api()
    hass = _build_hass()
    api = VThermAPI.get_vtherm_api(hass)
    api.register_feature_manager(FakeFeatureManagerFactory("auto_fan"))

    VThermAPI.reset_vtherm_api()

    recreated_api = VThermAPI.get_vtherm_api(hass)

    assert recreated_api is not api
    assert recreated_api.list_feature_managers() == []

    VThermAPI.reset_vtherm_api()
