""" Some constants for the VThermAPI library """

from datetime import datetime
from homeassistant.util import dt as dt_util
from homeassistant.core import HomeAssistant
DEVICE_MANUFACTURER = "JMCOLLIN"
DEVICE_MODEL = "Versatile Thermostat"

DOMAIN = "versatile_thermostat"

VTHERM_API_NAME = "vtherm_api"


def get_tz(hass: HomeAssistant):
    """Get the current timezone"""

    return dt_util.get_time_zone(hass.config.time_zone)


class NowClass:
    """For testing purpose only"""

    @staticmethod
    def get_now(hass: HomeAssistant) -> datetime:
        """A test function to get the now.
        For testing purpose this method can be overriden to get a specific
        timestamp.
        """
        return datetime.now(get_tz(hass))
