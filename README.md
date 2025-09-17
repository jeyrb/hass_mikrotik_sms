[![Rhizomatics Open Source](https://avatars.githubusercontent.com/u/162821163?s=96&v=4)](https://github.com/rhizomatics)

# Mikrotik SMS Notifier

Notify implementation using the SMS service provided by an LTE modem on Mikrotik routers.

## Features

- Send SMS notifications via Mikrotik LTE modem
- Supports multiple recipients
- Filters invalid, premium-rate, and international numbers
- Customizable country code restrictions
- Easy integration with Home Assistant via HACS
- Optionally use E.164 international style phone numbers

## Setup

### Prerequisites

- Home Assistant installed and running
- Mikrotik router with LTE modem and SMS capability
- HACS (Home Assistant Community Store) installed

### Installation

1. Register this GitHub repo as a custom repo
in your [HACS]( https://hacs.xyz) configuration.
2. Install the integration via HACS.

### Configuration

A username and password is required on the Mikrotik router.

Configure in the main Home Assistant config yaml, or an included notify.yaml

```yaml
- name: Mikrotik SMS
  platform: mikrotik_sms
  host: 192.168.88.200 # LAN IP Address of your Mikrotik router
  username: !secret mikrotik_user
  password: !secret mikrotik_password
  port: lte1
  ban_premium: true # default
  country_codes_allowed: 91, 43 # automatically adds country code for Home Assistant configured region
```

Add the user and password credentials to the HomeAssistant `secrets.yaml` file

```yaml
mikrotik_user: your_username
mikrotik_password: your_password
```

## Options

- An `smscentre` can be configured if needed by mobile provider
- `timeout` can be changed from the default 20 seconds to another value in seconds
- `ban_premium` can be set to `false` to allow sending to premium-rate
- `country_codes_allowed` can be set to a comma-separated list of country codes to allow sending to those countries. If not set, only the country code configured in Home Assistant is allowed.
  - To allow calling to any international code, use `0` as the wildcard country code.
- In the notification data section, `type` and `channel` can optionally be specified.
  - See the Mikrotik documentation for understanding of those.


## Reference
https://wiki.mikrotik.com/wiki/Manual:Tools/Sms

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## License

[Apache 2.0 License](LICENSE)
