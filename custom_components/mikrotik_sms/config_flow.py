from homeassistant import config_entries
from . import DOMAIN, CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_PORT, CONF_SMSC
from . import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USERNAME
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


DATA_SCHEMA = vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): str,
                    vol.Optional(CONF_SMSC): str,
                }
            )


class MikrotikSmsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
            """Handle user step."""

            return self.async_show_form(step_id="init", data_schema=DATA_SCHEMA)