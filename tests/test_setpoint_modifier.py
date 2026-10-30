"""Tests for the optional regulated temperature modifier contract."""

# pylint: disable=too-few-public-methods

from __future__ import annotations

import inspect

from src import vtherm_api
from src.vtherm_api.interfaces import InterfaceFeatureManager
from src.vtherm_api.setpoint_modifier import InterfaceSetpointModifier


class PlainFeatureManager:
    """A feature manager which does not adjust the regulated temperature."""

    name = "plain"


class RampingFeatureManager:
    """A feature manager which lowers the regulated temperature."""

    name = "ramping"

    def adjust_regulated_temperature(self, desired: float, regulation_step: float, command_cause: str | None) -> float | None:
        """Lower the regulated temperature by one step."""
        return desired - regulation_step


def test_protocol_is_exported() -> None:
    assert vtherm_api.InterfaceSetpointModifier is InterfaceSetpointModifier
    assert "InterfaceSetpointModifier" in vtherm_api.__all__


def test_protocol_has_a_single_method() -> None:
    assert set(InterfaceSetpointModifier.__protocol_attrs__) == {"adjust_regulated_temperature"}
    assert list(inspect.signature(InterfaceSetpointModifier.adjust_regulated_temperature).parameters) == ["self", "desired", "regulation_step", "command_cause"]


def test_feature_manager_protocol_is_unchanged() -> None:
    assert "adjust_regulated_temperature" not in InterfaceFeatureManager.__protocol_attrs__


def test_capability_is_detected_on_the_manager() -> None:
    assert isinstance(RampingFeatureManager(), InterfaceSetpointModifier)
    assert not isinstance(PlainFeatureManager(), InterfaceSetpointModifier)
    assert hasattr(RampingFeatureManager(), "adjust_regulated_temperature")
    assert not hasattr(PlainFeatureManager(), "adjust_regulated_temperature")


def test_modifier_returns_the_adjusted_temperature() -> None:
    assert RampingFeatureManager().adjust_regulated_temperature(21.0, 0.5, None) == 20.5
