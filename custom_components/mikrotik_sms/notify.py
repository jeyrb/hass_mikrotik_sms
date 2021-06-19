
import logging
import routeros_api

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    SERVICE_NOTIFY,
    BaseNotificationService,
)
from . import DOMAIN, CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_PORT, CONF_SMSC

_LOGGER = logging.getLogger(__name__)


def get_service(hass, config, discovery_info=None):
    return MikrotikSMSNotificationService(hass, config)


class MikrotikSMSNotificationService(BaseNotificationService):
    """Implement MikroTik SMS notification service."""

    def __init__(self, hass, config):
        """Initialize the service."""
        self.hass = hass
        self.config = config

    async def async_send_message(self, message="", **kwargs):
        """Send a message via mikrotik router."""
        _LOGGER.debug("Message: %s, kwargs: %s", message, kwargs)
        targets = kwargs.get(ATTR_TARGET)

        conn = routeros_api.RouterOsApiPool(self.config[CONF_HOST], 
                                            self.config[CONF_USERNAME], 
                                            self.config[CONF_PASSWORD],
                                            plaintext_login=True)
        api = conn.get_api()
        for target in targets:
            r = api.get_resource("/").call(
                "tool/sms/send", {"port": self.config[CONF_PORT], 
                                  "smsc": self.config[CONF_SMSC], 
                                  "phone-number": target, 
                                  "message": message}
            )
            _LOGGER.debug('MIKROSMS Sent to %s with response %s', target, r)
        conn.disconnect()
 