
import logging

import asyncio
import async_timeout

from homeassistant.components.notify import (
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    SERVICE_NOTIFY,
    BaseNotificationService,
)


from . import (
    CONF_HOST,
    CONF_PORT,
    CONF_SMSC,
    CONF_USERNAME,
    DOMAIN,
    get_conn,
)

_LOGGER = logging.getLogger(__name__)

# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(DATA_SCHEMA)


def get_service(hass, config, discovery_info=None):
    hass.states.async_set('%s.configured' % DOMAIN, True, {
        CONF_HOST: config.get(CONF_HOST),
        CONF_PORT: config.get(CONF_PORT),
        CONF_USERNAME: config.get(CONF_USERNAME),
        CONF_SMSC: config.get(CONF_SMSC),
    })
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

        conn = get_conn(self.config)
        for target in targets:
            try:
                with async_timeout.timeout(20):
                    _LOGGER.debug('MIKROSMS %s',self.config)
                    r = conn.get_api().get_resource("/").call(
                        "tool/sms/send", {"port": self.config[CONF_PORT],
                                          "smsc": str(self.config.get(CONF_SMSC)),
                                          "phone-number": str(target),
                                          "message": message}
                    )
                    _LOGGER.debug('MIKROSMS Sent to %s with response %s', target, r)
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout accessing Mikrotik at %s", self.config[CONF_HOST])

        conn.disconnect()
