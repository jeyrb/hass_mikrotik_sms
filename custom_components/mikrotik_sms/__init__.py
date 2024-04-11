"""The Mikrotik SMS notification integration"""

import logging

DOMAIN = "mikrotik_sms"

PLATFORMS = ["notify"]

DEFAULT_HOST = "192.168.88.200"
DEFAULT_USERNAME = "hass"
DEFAULT_PORT = "lte1"
CONF_SMSC = "smscentre"
CONF_TIMEOUT = "timeout"
CONF_COUNTRY_CODES_ALLOWED = "country_codes_allowed"
CONF_BAN_PREMIUM = "ban_premium"

_LOGGER = logging.getLogger(__name__)
