
import asyncio
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

        conn = routeros_api.RouterOsApiPool("192.168.88.200", 
                                            username="hass", 
                                            password="xP3gF3BzE6oA7@KsE2Y}", 
                                            plaintext_login=True)
        api = conn.get_api()
        for target in targets:
            r = api.get_resource("/").call(
                "tool/sms/send", {"port": "lte1", "smsc": "+447782000800", 
                                    "phone-number": target, 
                                    "message": message}
            )
            _LOGGER.debug('MIKROSMS Sent to %s with response %s', target, r)
        conn.disconnect()
 