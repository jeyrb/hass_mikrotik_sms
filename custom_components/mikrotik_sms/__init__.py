""" The Mikrotik SMS notification integration """

DOMAIN = "mikrtotik_sms"

CONF_HOST = "routeraddress"
DEFAULT_HOST = '192.188.100.200'
CONF_USERNAME = "username"
DEFAULT_USERNAME = 'hass'
CONF_PASSWORD = "password"
CONF_PORT = "modemport"
DEFAULT_PORT = 'lte1'
CONF_SMSC = "smscentre"

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    hass.states.async_set("mikrotik_sms.configured", True)
    return True