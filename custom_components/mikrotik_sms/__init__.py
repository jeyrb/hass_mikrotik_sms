""" The Mikrotik SMS notification integration """

import logging

DOMAIN = "mikrotik_sms"

PLATFORMS = ["notify"]

DEFAULT_HOST = '192.168.88.200'
DEFAULT_USERNAME = 'hass'
DEFAULT_PORT = 'lte1'
CONF_SMSC = "smscentre"
CONF_TIMEOUT = "timeout"

_LOGGER = logging.getLogger(__name__)


