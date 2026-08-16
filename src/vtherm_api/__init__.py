"""Public package for the Versatile Thermostat API."""

from .interfaces import (
    InterfaceCycleScheduler,
    InterfaceFeatureManager,
    InterfaceFeatureManagerFactory,
    InterfacePropAlgorithmFactory,
    InterfacePropAlgorithmHandler,
    InterfaceThermostat,
    InterfaceThermostatRuntime,
)
from .plugin_climate import PluginClimate
from .vtherm_api import VThermAPI

__version__ = "0.4.0b1"

__all__ = [
    "InterfaceCycleScheduler",
    "InterfaceFeatureManager",
    "InterfaceFeatureManagerFactory",
    "InterfacePropAlgorithmFactory",
    "InterfacePropAlgorithmHandler",
    "InterfaceThermostat",
    "InterfaceThermostatRuntime",
    "PluginClimate",
    "VThermAPI",
    "__version__",
]
