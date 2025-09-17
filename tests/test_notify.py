from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.mikrotik_sms.notify import DisallowedNumber, InvalidNumber, MikrotikSMSNotificationService


async def test_send_message() -> None:
    hass = Mock()
    hass.states = Mock()
    hass.config.country = "GB"
    hass.services.async_call = AsyncMock()
    with patch("custom_components.mikrotik_sms.notify.routeros_api.RouterOsApiPool") as mock_api:
        uut = MikrotikSMSNotificationService(
            hass,
            host="127.0.0.1",
            port="lte5",
            username="mikro_test",
            password="mikro_pass",  # noqa: S106
            timeout=10,
        )

        await uut.initialize()
        mock_api.assert_called_with("127.0.0.1", "mikro_test", "mikro_pass", plaintext_login=True)

        await uut.async_send_message(message="testing 123", target=["+441234999888"], data={"type": "ussd"})
        mock_call = mock_api().get_api().get_resource().call
        mock_call.assert_called_with(
            "tool/sms/send", {"port": "lte5", "phone-number": "+441234999888", "message": "testing 123", "type": "ussd"}
        )


def test_phone_number_checks() -> None:
    hass = Mock()
    hass.config.country = "GB"
    uut = MikrotikSMSNotificationService(hass)
    assert uut.validated_number("07386404283") == "+447386404283"
    assert uut.validated_number("+447386404283") == "+447386404283"
    with pytest.raises(InvalidNumber):
        uut.validated_number("010 5932 8484 1234")
    with pytest.raises(DisallowedNumber):
        uut.validated_number("+917386404283")
    with pytest.raises(DisallowedNumber):
        uut.validated_number("090 5932 1234")

    uut = MikrotikSMSNotificationService(hass, country_codes_allowed=[91])
    assert uut.validated_number("+917386404283") == "+917386404283"
