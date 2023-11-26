""" The Mikrotik SMS notification integration """

import logging

import routeros_api


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "mikrotik_sms"

PLATFORMS = ["notify"]

CONF_HOST = "host"
DEFAULT_HOST = '192.168.88.200'
CONF_USERNAME = "username"
DEFAULT_USERNAME = 'hass'
CONF_PASSWORD = "password"
CONF_PORT = "port"
DEFAULT_PORT = 'lte1'
CONF_SMSC = "smscentre"

_LOGGER = logging.getLogger(__name__)

def get_conn(config):
    _LOGGER.info('MIKROSMS Connecting to %s as %s', config[CONF_HOST], config[CONF_USERNAME])
    conn = routeros_api.RouterOsApiPool(config[CONF_HOST],
                                        config[CONF_USERNAME],
                                        config[CONF_PASSWORD],
                                        plaintext_login=True)
    return conn


