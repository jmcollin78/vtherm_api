# custom_components/versatile_thermostat/thermostat_interface.py
from __future__ import annotations
from typing import Any
from datetime import datetime

from typing import Protocol, runtime_checkable
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant, CALLBACK_TYPE

from .commons_type import ConfigData


@runtime_checkable
class InterfaceThermostat(Protocol):
    """Contrat minimal commun pour manipuler un thermostat VTherm."""

    @property
    def name(self) -> str:
        """Get the name of the thermostat."""
        ...

    def register_manager(self, manager: InterfaceFeatureManager):
        """Register a feature manager to the thermostat."""
        ...

    async def service_download_logs(
        self,
        log_level: str = "DEBUG",
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ):
        """Service to download logs from the thermostat."""
        ...

    @property
    def unique_id(self) -> str:
        """Get the unique ID of the thermostat."""
        ...

    @property
    def device_info(self) -> DeviceInfo | None:
        """Get the device information."""
        ...


@runtime_checkable
class InterfaceFeatureManager(Protocol):
    """Contrat commun pour tous les FeatureManagers."""

    def post_init(self, entry_infos: ConfigData | dict[str, Any]) -> None:
        """Initialise le manager avec la configuration fusionnée."""
        ...

    async def start_listening(self, force: bool = False) -> None:
        """Abonne le manager aux événements nécessaires."""
        ...

    def stop_listening(self) -> bool | None:
        """Désabonne les listeners du manager."""
        ...

    async def refresh_state(self) -> bool:
        """Rafraîchit l'état interne et retourne True si changement."""
        ...

    def restore_state(self, old_state: Any) -> None:
        """Restaure l'état du manager depuis un ancien state HA."""
        ...

    def add_listener(self, func: CALLBACK_TYPE) -> None:
        """Ajoute un callback à désinscrire au stop."""
        ...

    @property
    def is_configured(self) -> bool:
        """Le manager est-il correctement configuré ?"""
        ...

    @property
    def is_detected(self) -> bool:
        """Le manager détecte-t-il actuellement sa condition ?"""
        ...

    @property
    def name(self) -> str:
        """Nom logique du manager."""
        ...

    @property
    def hass(self) -> HomeAssistant:
        """Instance Home Assistant."""
        ...
