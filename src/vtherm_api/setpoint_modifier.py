"""Regulated temperature modifier contract.

An ``over_climate`` thermostat computes a regulated temperature (the target
temperature plus the self-regulation offset) and sends it to the underlying
climate entities. This module defines the contract that lets a feature manager
provided by a plugin adjust that temperature before it is sent, for example to
limit how fast it moves.

The contract is optional. It lives in a dedicated protocol,
:class:`InterfaceSetpointModifier`, next to the unchanged
:class:`InterfaceFeatureManager`. A feature manager that does not implement it
keeps satisfying :class:`InterfaceFeatureManager`; the core detects the
capability with ``hasattr(manager, "adjust_regulated_temperature")``.

Rules of the contract:

* The method is called only on a feature manager whose ``is_configured`` is
  True, each time the thermostat computes the regulated temperature: after the
  self-regulation, and before the core adds the device temperature offset,
  rounds to ``regulation_step``, filters a change smaller than the regulation
  delta and sends the result. The regulation period, the delta filter and the
  cycle stay under the control of the core.
* ``desired`` is the regulated temperature computed by the core.
  ``regulation_step`` is the step the core rounds to: a plugin that moves the
  temperature by less than this step would see its change swallowed.
  ``command_cause`` is the cause of the command, ``None`` for a regular
  regulation and ``"underlying_tracking"`` when the thermostat follows a change
  made on the device itself.
* The method returns the temperature to use. Returning ``None`` keeps
  ``desired``.
* The method is a plain function, not a coroutine: it must be quick and must not
  block. The thermostat is switched from OFF to heat or cool only after the
  temperature returned here has been sent to the underlyings, so that the device
  does not start at its own stored setpoint. This does not happen when the
  device itself changed its mode (``command_cause`` is ``"underlying_tracking"``).
* A plugin sees the thermostat go OFF through ``refresh_state`` of its feature
  manager, which the core calls on every control cycle.
* An exception raised by the method is logged and does not break the
  regulation: the value of ``desired`` is used.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class InterfaceSetpointModifier(Protocol):
    """Optional feature manager extension adjusting the regulated temperature."""

    def adjust_regulated_temperature(
        self,
        desired: float,
        regulation_step: float,
        command_cause: str | None,
    ) -> float | None:
        """Return the temperature to send to the underlyings, or None to keep ``desired``."""
        ...
