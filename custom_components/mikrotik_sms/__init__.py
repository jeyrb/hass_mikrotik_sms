""" The Mikrotik SMS notification integration """

import logging

import routeros_api
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

DOMAIN = "mikrotik_sms"

PLATFORMS = ["notify"]

DEFAULT_HOST = '192.168.88.200'
DEFAULT_USERNAME = 'hass'
DEFAULT_PORT = 'lte1'
CONF_SMSC = "smscentre"
CONF_TIMEOUT = "timeout"

_LOGGER = logging.getLogger(__name__)


def get_conn(config):
    _LOGGER.info('MIKROSMS Connecting to %s as %s',
                 config[CONF_HOST], config[CONF_USERNAME])
    conn = routeros_api.RouterOsApiPool(config[CONF_HOST],
                                        config[CONF_USERNAME],
                                        config[CONF_PASSWORD],
                                        plaintext_login=True)
    return conn
