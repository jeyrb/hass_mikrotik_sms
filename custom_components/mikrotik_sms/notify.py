import logging

import asyncio
import async_timeout
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_TARGET,
    ATTR_DATA,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)


from . import (
    CONF_HOST,
    CONF_PORT,
    CONF_SMSC,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_USERNAME,
    DEFAULT_PORT,
    get_conn,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): str,
        vol.Optional(CONF_SMSC): str,
    }
)


def get_service(hass, config, discovery_info=None):
    hass.states.async_set(
        "%s.configured" % DOMAIN,
        True,
        {
            CONF_HOST: config.get(CONF_HOST),
            CONF_PORT: config.get(CONF_PORT),
            CONF_USERNAME: config.get(CONF_USERNAME),
            CONF_SMSC: config.get(CONF_SMSC),
        },
    )
    return MikrotikSMSNotificationService(hass, config)


class MikrotikSMSNotificationService(BaseNotificationService):
    """Implement MikroTik SMS notification service."""

    def __init__(self, hass, config):
        """Initialize the service."""
        self.hass = hass
        self.config = config
        self.validate_connection()

    def validate_connection(self):
        conn = get_conn(self.config)
        r = conn.get_api().get_resource("/").call("tool/sms/print")
        _LOGGER.debug("Connected: %s", r)

    async def async_send_message(self, message="", **kwargs):
        """Send a message via mikrotik router."""
        _LOGGER.debug("Message: %s, kwargs: %s", message, kwargs)
        targets = kwargs.get(ATTR_TARGET)
        data = kwargs.get(ATTR_DATA)
        if not targets:
            _LOGGER.info("At least 1 target phone number is required")
            return
        if len(message) > 160:
            _LOGGER.warning("Message > 160 (%s chars), truncating" % len(message))
            message = message[:160]
        channel = sms_type = None
        if data:
            channel = data["channel"] if "channel" in data else None
            sms_type = data["type"] if "type" in data else None
            if sms_type not in ("ussd", "class-0", "class-1", None):
                _LOGGER.warning("Unknown SMS type %s" % sms_type)

        conn = None
        try:
            conn = get_conn(self.config)
            for target in targets:
                try:
                    payload = {
                        "port": self.config[CONF_PORT],
                        "smsc": str(self.config.get(CONF_SMSC)),
                        "phone-number": str(target),
                        "message": message,
                    }
                    if channel is not None:
                        payload["channel"] = channel
                    if sms_type is not None:
                        payload["type"] = sms_type

                    with async_timeout.timeout(20):
                        _LOGGER.debug("MIKROSMS %s" % self.config)
                        r = conn.get_api().get_resource("/").call("tool/sms/send", payload)
                        _LOGGER.debug("MIKROSMS Sent to %s with response %s", target, r)
                except asyncio.TimeoutError:
                    _LOGGER.error(
                        "Timeout accessing Mikrotik at %s", self.config[CONF_HOST]
                    )
        finally:
            if conn is not None:
                conn.disconnect()
