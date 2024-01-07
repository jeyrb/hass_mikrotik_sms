# Mikrotik SMS Notifier

Notify using SMS service via LTE modem on a Mikrotik router.

Sends to multiple notify targets, where each target is a phone number, 
optionally using E.164 international style.

## Setup

Register this GitHub repo as a custom repo 
un your [HACS]( https://hacs.xyz) configuration. 

A username and password is required on the Mikrotik router. 

Configure in the main Home Assistant config yaml, or an included notify.yaml

```yaml
- name: Mikrotik SMS
  platform: mikrotik_sms
  host: 192.168.88.200
  username: !secret mikrotik_user
  password: !secret mikrotik_password
  port: lte1
```

With the user and password added to the HomeAssistant `secrets.yaml` file

Optionally an `smscentre` can also be configured.

## Options

In the notification data section, `type` and `channel` can optionally be specified.
See the Mikrotik documentation for understanding of those.

## Reference
https://wiki.mikrotik.com/wiki/Manual:Tools/Sms