from unittest.mock import AsyncMock, Mock, patch
from custom_components.mikrotik_sms.notify import MikrotikSMSNotificationService


async def test_send_message() -> None:
    hass = Mock()
    hass.states = Mock()
    hass.services.async_call = AsyncMock()
    with patch("custom_components.mikrotik_sms.notify.routeros_api.RouterOsApiPool") as mock_api:
        uut = MikrotikSMSNotificationService(
            hass, host="127.0.0.1", port=9000,
            username="mikro_test", password="mikro_pass",
            timeout=10)

        await uut.initialize()
        mock_api.assert_called_with(
            "127.0.0.1", "mikro_test", "mikro_pass", plaintext_login=True)

        await uut.async_send_message(message="testing 123",
                                     target=["+441234999888"],
                                     data={
                                         "type": "ussd"
                                     })
        mock_call = mock_api().get_api().get_resource().call
        mock_call.assert_called_with("tool/sms/send",
                                     {'port': 9000,
                                      'phone-number': '+441234999888',
                                      'message': 'testing 123',
                                      'type': 'ussd'})
