""" The Mikrotik SMS notification integration """

import logging

import routeros_api
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SERVICE_RELOAD
from homeassistant.core import HomeAssistant
from homeassistant.components import notify as hass_notify

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

DATA_SCHEMA = vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): str,
                    vol.Optional(CONF_SMSC): str,
                }
            )

_LOGGER = logging.getLogger(__name__)

def get_api(config):
    _LOGGER.info('MIKROSMS Connecting to %s as %s', config[CONF_HOST], config[CONF_USERNAME])
    conn = routeros_api.RouterOsApiPool(config[CONF_HOST],
                                        config[CONF_USERNAME],
                                        config[CONF_PASSWORD],
                                        plaintext_login=True)
    return conn.get_api()


