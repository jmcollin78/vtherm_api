"""Public package for the Versatile Thermostat API."""

from .interfaces import (
    InterfaceCycleScheduler,
    InterfaceFeatureManager,
    InterfacePropAlgorithmFactory,
    InterfacePropAlgorithmHandler,
    InterfaceThermostat,
    InterfaceThermostatRuntime,
)
from .plugin_climate import PluginClimate
from .vtherm_api import VThermAPI

__version__ = "0.2.1"

__all__ = [
    "InterfaceCycleScheduler",
    "InterfaceFeatureManager",
    "InterfacePropAlgorithmFactory",
    "InterfacePropAlgorithmHandler",
    "InterfaceThermostat",
    "InterfaceThermostatRuntime",
    "PluginClimate",
    "VThermAPI",
    "__version__",
]
