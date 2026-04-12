""" The API of Versatile Thermostat"""
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.components.climate import ClimateEntity, DOMAIN as CLIMATE_DOMAIN

from .const import DOMAIN, VTHERM_API_NAME, CONF_NAME, NowClass
from .log_collector import get_vtherm_logger
from .plugin_climate import PluginClimate

_LOGGER = get_vtherm_logger(__name__)


class VThermAPI:
    """The VThermAPI
    This class is a singleton that provides access to the VTherm API instance through HA hass mecanism. It also provides a reference to the HA instance for use in the API implementation.
    """

    _hass: HomeAssistant = None

    def __init__(self) -> None:
        """Initialize the VThermAPI instance."""
        self._now: datetime = None

    @classmethod
    def get_vtherm_api(cls, hass=None):
        """Get the eventual VTherm API class instance or
        instantiate it if it doesn't exists"""
        if hass is not None:
            VThermAPI._hass = hass

        if VThermAPI._hass is None:
            return None

        domain = VThermAPI._hass.data.get(DOMAIN)
        if not domain:
            VThermAPI._hass.data.setdefault(DOMAIN, {})

        ret = VThermAPI._hass.data.get(
            DOMAIN).get(VTHERM_API_NAME)
        if ret is None:
            ret = VThermAPI()
            VThermAPI._hass.data[DOMAIN][VTHERM_API_NAME] = ret
        return ret

    @classmethod
    def reset_vtherm_api(cls):
        """Reset the VTherm API instance and related data."""
        if VThermAPI._hass is None:
            return

        # Remove the API instance from hass.data
        if DOMAIN in VThermAPI._hass.data:
            VThermAPI._hass.data[DOMAIN].pop(
                VTHERM_API_NAME, None)
        VThermAPI._hass = None

    def add_entry(self, entry: ConfigEntry):
        """Add a new entry"""
        name = entry.data.get(CONF_NAME)
        _LOGGER.debug("%s - Add the entry %s - %s", name, entry.entry_id, name)
        # Add the entry in hass.data
        VThermAPI._hass.data[DOMAIN][entry.entry_id] = entry

    def remove_entry(self, entry: ConfigEntry):
        """Remove an entry"""
        name = entry.data.get(CONF_NAME)
        _LOGGER.debug("%s - Remove the entry %s - %s",
                      name, entry.entry_id, name)
        VThermAPI._hass.data[DOMAIN].pop(entry.entry_id)
        # If not more entries are preset, remove the API
        if (len([
            val
            for val in VThermAPI._hass.data[DOMAIN].values()
            if isinstance(val, ConfigEntry)
        ]) == 0):
            _LOGGER.debug("No more entries-> Remove the API from DOMAIN")
            if DOMAIN in VThermAPI._hass.data:
                VThermAPI._hass.data.pop(DOMAIN)

    @property
    def hass(self):
        """Get the HomeAssistant object"""
        return VThermAPI._hass

    @property
    def name(self) -> str:
        """Get the name of the API"""
        return "VThermAPI"

    # For testing purpose
    def _set_now(self, now: datetime):
        """Set the now timestamp. This is only for tests purpose"""
        self._now = now

    @property
    def now(self) -> datetime:
        """Get now. The local datetime or the overloaded _set_now date"""
        return self._now if self._now is not None else NowClass.get_now(self._hass)

    def link_to_vtherm(self, vtherm, plugin_vtherm_entity_id: str):
        """Link the VTherm API to a specific VTherm entity."""
        # Implementation for linking to a VTherm entity
        # Find a vtherm instance of type PluginClimate in hass
        component: EntityComponent[ClimateEntity] = self._hass.data.get(
            CLIMATE_DOMAIN, None)
        if component:
            for entity in list(component.entities):
                try:
                    if entity.device_info and entity.device_info.get("model", None) == DOMAIN:
                        if plugin_vtherm_entity_id == entity.entity_id and entity.__class__.__name__ == "PluginClimate":
                            plugin_climate: PluginClimate = entity
                            _LOGGER.info(
                                "%s - We have found the linked PluginVTherm", self)
                            plugin_climate.link_to_vtherm(vtherm)
                            return
                except Exception as e:  # pylint: disable=broad-except
                    _LOGGER.error(
                        "Error searching/initializing entity %s: %s", entity.entity_id, e)
