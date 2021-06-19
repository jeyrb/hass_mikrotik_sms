#!/usr/local/bin/python
# coding=utf-8
import routeros_api


def send_sms(num, mes):

    conn = routeros_api.RouterOsApiPool("192.168.88.200", username="hass", password="xP3gF3BzE6oA7@KsE2Y}", plaintext_login=True)
    api = conn.get_api()
    r = api.get_resource("/").call(
        "tool/sms/send", {"port": "lte1", "smsc": "+447782000800", "phone-number": str(num), "message": mes}
    )
    print(r)
    conn.disconnect()


if __name__ == "__main__":
    import sys

    num = str(sys.argv[1])
    mes = str(sys.argv[2])
    send_sms(num, mes)

# %%
