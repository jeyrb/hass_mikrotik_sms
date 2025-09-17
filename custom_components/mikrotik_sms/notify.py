import logging

import async_timeout
import routeros_api  # type: ignore
import voluptuous as vol
from homeassistant.components.notify import ATTR_DATA, ATTR_TARGET, PLATFORM_SCHEMA, BaseNotificationService
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
    PhoneNumberType,
    country_code_for_region,
    format_number,
    is_valid_number,
    number_type,
    parse,
)

from . import (
    CONF_BAN_PREMIUM,
    CONF_COUNTRY_CODES_ALLOWED,
    CONF_SMSC,
    CONF_TIMEOUT,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_USERNAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.NOTIFY]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): str,
    vol.Optional(CONF_SMSC): str,
    vol.Optional(CONF_TIMEOUT, default=20): int,
    vol.Optional(CONF_COUNTRY_CODES_ALLOWED, default=[]): vol.All(cv.ensure_list, [cv.positive_int]),
    vol.Optional(CONF_BAN_PREMIUM, default=True): bool,
})


class MikrotikSMSNotificationService(BaseNotificationService):
    """Implement MikroTik SMS notification service."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str | None = None,
        port: str | None = DEFAULT_PORT,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 20,
        smsc: str | None = None,
        country_codes_allowed: list[int] | None = None,
        ban_premium: bool = True,
    ) -> None:
        """Initialize the service."""
        self.hass = hass
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.smsc = str(smsc) if smsc is not None else None
        self.timeout = timeout
        self.region = hass.config.country
        self.ban_premium = ban_premium
        self.country_codes_allowed = country_codes_allowed or []
        if self.region:
            self.country_codes_allowed.append(country_code_for_region(self.region))

    async def initialize(self) -> None:
        await self.validate_connection()

    def get_conn(self) -> routeros_api.RouterOsApiPool:
        if self.username is None or self.password is None:
            _LOGGER.error("MIKROSMS Username or Password not set")
            raise ValueError("MIKROSMS Username or Password not set")
        _LOGGER.info("MIKROSMS Connecting to %s as %s", self.host, self.username)
        return routeros_api.RouterOsApiPool(self.host, self.username, self.password, plaintext_login=True)

    async def validate_connection(self) -> None:
        conn = self.get_conn()
        async with async_timeout.timeout(self.timeout):
            r = conn.get_api().get_resource("/").call("tool/sms/print")
        _LOGGER.debug("Connected: %s", r)

    async def async_send_message(self, message: str = "", **kwargs) -> None:
        """Send a message via mikrotik router."""
        _LOGGER.debug("Message: %s, kwargs: %s", message, kwargs)
        targets = kwargs.get(ATTR_TARGET)
        data = kwargs.get(ATTR_DATA)
        if not targets:
            _LOGGER.info("At least 1 target phone number is required")
            return
        if len(message) > 160:
            _LOGGER.warning("Message > 160 (%s chars), truncating", len(message))
            message = message[:160]
        channel = sms_type = None
        if data:
            channel = data.get("channel")
            sms_type = data.get("type")
            if sms_type not in ("ussd", "class-0", "class-1", None):
                _LOGGER.warning("Unknown SMS type %s", sms_type)

        conn: routeros_api.RouterOsApiPool | None = None
        try:
            conn = self.get_conn()
            for target in targets:
                try:
                    payload = {
                        "port": self.port,
                        "phone-number": self.validated_number(target),
                        "message": message,
                    }
                    if channel is not None:
                        payload["channel"] = channel
                    if sms_type is not None:
                        payload["type"] = sms_type
                    if self.smsc is not None:
                        payload["smsc"] = self.smsc

                    async with async_timeout.timeout(self.timeout):
                        _LOGGER.debug("MIKROSMS %s:%s", self.host, self.port)
                        r = conn.get_api().get_resource("/").call("tool/sms/send", payload)
                        _LOGGER.debug("MIKROSMS Sent to %s with response %s, payload: %s", target, r, payload)
                except TimeoutError:
                    _LOGGER.error("Timeout accessing Mikrotik at %s:%s", self.host, self.port)
        finally:
            if conn is not None:
                conn.disconnect()

    def validated_number(self, number: str | int) -> str:
        try:
            phone_number = parse(str(number), self.region)
            if not is_valid_number(phone_number):
                raise InvalidNumber(f"Invalid phone number {number}")
            if phone_number.country_code not in self.country_codes_allowed and 0 not in self.country_codes_allowed:
                raise DisallowedNumber(f"Disallowed country code {phone_number.country_code}")
            if self.ban_premium and number_type(phone_number) == PhoneNumberType.PREMIUM_RATE:
                _LOGGER.warning("Disallowed premium rate number %s", number)
                raise DisallowedNumber(f"Disallowed premium rate number {number}")
            return format_number(phone_number, PhoneNumberFormat.E164)
        except NumberParseException as e:
            _LOGGER.error("Invalid phone number %s: %s", number, e)
            raise InvalidNumber(e) from e


class DisallowedNumber(BaseException):
    pass


class InvalidNumber(BaseException):
    pass


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,  # noqa: ARG001
) -> MikrotikSMSNotificationService:
    hass.states.async_set(
        f"{DOMAIN}.configured",
        True,
        {
            CONF_HOST: config.get(CONF_HOST),
            CONF_PORT: config.get(CONF_PORT),
            CONF_USERNAME: config.get(CONF_USERNAME),
            CONF_SMSC: config.get(CONF_SMSC),
            CONF_COUNTRY_CODES_ALLOWED: config.get(CONF_COUNTRY_CODES_ALLOWED),
            CONF_BAN_PREMIUM: config.get(CONF_BAN_PREMIUM),
        },
    )
    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)
    service = MikrotikSMSNotificationService(
        hass,
        config.get(CONF_HOST),
        config.get(CONF_PORT),
        config.get(CONF_USERNAME),
        config.get(CONF_PASSWORD),
        config.get(CONF_TIMEOUT, 10),
        config.get(CONF_SMSC),
        config.get(CONF_COUNTRY_CODES_ALLOWED),
        config.get(CONF_BAN_PREMIUM, True),
    )
    await service.initialize()
    return service
