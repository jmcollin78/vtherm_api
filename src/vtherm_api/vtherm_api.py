
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VTHERM_API_NAME
from .log_collector import get_vtherm_logger

_LOGGER = get_vtherm_logger(__name__)


class VersatileThermostatAPI:
    """The VersatileThermostatAPI"""

    _hass: HomeAssistant = None

    @classmethod
    def get_vtherm_api(cls, hass=None):
        """Get the eventual VTherm API class instance or
        instantiate it if it doesn't exists"""
        if hass is not None:
            VersatileThermostatAPI._hass = hass

        if VersatileThermostatAPI._hass is None:
            return None

        domain = VersatileThermostatAPI._hass.data.get(DOMAIN)
        if not domain:
            VersatileThermostatAPI._hass.data.setdefault(DOMAIN, {})

        ret = VersatileThermostatAPI._hass.data.get(
            DOMAIN).get(VTHERM_API_NAME)
        if ret is None:
            ret = VersatileThermostatAPI()
            VersatileThermostatAPI._hass.data[DOMAIN][VTHERM_API_NAME] = ret
        return ret
