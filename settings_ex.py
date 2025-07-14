'''
This file is used to configure the monitoring bot.
'''
import logging

#### Logging ####
LOG_FILE = "monitor.log" # Where should the log file live?
LOG_LEVEL = logging.WARNING # How verbose should logs be ("INFO", "WARNING", "ERROR", "CRITICAL")?
ASYNCIO_DEBUG = False # Verbose logging from asyncio

#### Websocket ####
WS_RETRY = 20 # number of seconds to wait between dropped WS connection checks
MAX_CONNECT_ATTEMPTS = 999999 # Max number of connection retries

PROCESSED_VAL_MAX = 10000 # Maximum number of validation messages to store to avoid duplicates
# when this number is reached, half of the validation message tracking list will be deleted.

MAX_VAL_STREAMS = 5 # Max validations streams to subscribe to. These produce a lot of messages.
# Client too slow WS disconnects, seemingly forked servers, and other unexpected behavior
# can result from excessive validation stream subscriptions. Too few streams can result in
# false missed validation messages.
# The above setting is ignored if no validators are defined for monitoring.

#### Fork Check ####
FORK_CHECK_FREQ = 10 # Number of seconds to wait between checks for forked servers
LL_FORK_CUTOFF = 25 # Number ledgers ahead or behind mode of monitored servers to consider a fork

#### Console Output ####
CONSOLE_OUT = True # Print a fancy table to the console
CONSOLE_REFRESH_TIME = 5 # Time in seconds to wait before refreshing console output.
PRINT_AMENDMENTS = True # Print output summarizing amendment voting.

#### Random ####
REMOVE_DUP_VALIDATORS = True # Allow the same validator master/eph keys to be tracked more than once

LOG_VALIDATIONS_FROM = [] # Log validations that include a master_key defined in this list.

#### Amendments ####
AMENDMENTS = [
    {
        'id': '8CC0774A3BF66D1D22E76BBDA8E8A232E6B6313834301B3B23E8601196AE6455',
        'name': 'AMM',
    },
    {
        'id': 'C393B3AEEBF575E475F0C60D5E4241B2070CC4D0EB6C4846B1A07508FAEFC485',
        'name': 'fixInnerObjTemplate',
    },
    {
        'id': '15D61F0C6DB6A2F86BCF96F1E2444FEC54E705923339EC175BD3E517C8B3FF91',
        'name': 'fixDisallowIncomingV1',
    },
    {
        'id': '3318EA0CF0755AF15DAC19F2B5C5BCBFF4B78BDD57609ACCAABE2C41309B051A',
        'name': 'fixFillOrKill',
    },
    {
        'id': 'C98D98EE9616ACD36E81FDEB8D41D349BF5F1B41DD64A0ABC1FE9AA5EA267E9C',
        'name': 'XChainBridge',
    },
    {
        'id': 'DB432C3A09D9D5DFC7859F39AE5FF767ABC59AED0A9FB441E83B814D8946C109',
        'name': 'DID',
    },
    {
        'id': '93E516234E35E08CA689FA33A6D38E103881F8DCB53023F728C307AA89D515A7',
        'name': 'XRPFees',
    },
    {
        'id': '03BDC0099C4E14163ADA272C1B6F6FABB448CC3E51F522F978041E4B57D9158C',
        'name': 'fixNFTokenReserve',
    },
]

#### Administrative Notification ####
ADMIN_HEARTBEAT = False # should we send heartbeat messages to administrators?
HEARTBEAT_INTERVAL = 3600 # Time in seconds between heartbeat messages

#### General Notification Settings ####
KNOWN_NOTIFICATIONS = ['twilio', 'discord', 'mattermost', 'slack', 'smtp']

# Specify which notification methods will be enabled.
# Messages will be dropped if not enabled here, even if individual clients enable them.
SEND_TWILIO = False
SEND_DISCORD = False
SEND_MATTERMOST = False
SEND_SLACK = False
SEND_SMTP = False

# If TWILIO_ACCOUNT_SID and/or TWILIO_AUTH_TOKEN below are set to "None",
# they will be sourced from env variables of the same name (this is likely more secure).
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/" #Start with 'https' and end with a forward slash

# The following information is used to send administrative messages, such as routine heartbeats
# Phone numbers should be prefixed with a "+" and the country code (e.g., +1 for the USA).
ADMIN_NOTIFICATIONS = [
    {
        "admin_name": "Admin 1",
        "notifications": {
            "twilio": {
                "notify_twilio": False,
                "phone_numbers": [
                    {
                        "phone_from": "+19000000",
                        "phone_to": "+10000000",
                    },
                ],
            },

            "discord": {
                "notify_discord": True,
                "discord_servers": [
                    {
                        "discord_id": "",
                        "discord_token": "",
                    },
                ],
            },

            "mattermost": {
                "notify_mattermost": False,
                "mattermost_servers": [
                    {
                        "mattermost_url": "",
                        "mattermost_key": "",
                        "mattermost_channel": "",
                    }
                ]
            },

            "slack": {
                "notify_slack": False,
            },

            "smtp": {
                "notify_smtp": False,
            },
        },
    },
]


################################ Servers and Validators to Monitor ################################

############# Stock Servers
# These should be stock servers (validators typically should not allow inbound connections).
# As the number of servers in this array increases (up to MAX_VAL_STREAMS),
# the probability of a false missed validation from a below validator decreases
# (in other words, validation monitoring gets more accurate with more stock servers).

SERVERS = [
    {
        "url": "wss://xrplcluster.com:443",
        "server_name": "Cluster",
        "ssl_verify": True,
        "notifications": {
            "twilio": {
                "notify_twilio": False,
                "phone_numbers": [
                    {
                        "phone_from": "+19000000",
                        "phone_to": "+10000000",
                    },
                ],
            },

            "discord": {
                "notify_discord": False,
                "discord_servers": [
                    {
                        "discord_id": "",
                        "discord_token": "",
                    },
                ],
            },

            "mattermost": {
                "notify_mattermost": False,
            },

            "slack": {
                "notify_slack": False,
            },

            "smtp": {
                "notify_smtp": False,
            },
        },
    },

    {
        "url": "wss://s1.ripple.com:443",
        "server_name": "Ripple-S1",
        "ssl_verify": True,
        "notifications": {
            "twilio": {
                "notify_twilio": False,
                "phone_numbers": [
                    {
                        "phone_from": "+19000000",
                        "phone_to": "+10000000",
                    },
                ],
            },

            "discord": {
                "notify_discord": False,
                "discord_servers": [
                    {
                        "discord_id": "",
                        "discord_token": "",
                    },
                ],
            },

            "mattermost": {
                "notify_mattermost": False,
            },

            "slack": {
                "notify_slack": False,
            },

            "smtp": {
                "notify_smtp": False,
            },
        },
    },

    {
        "url": "wss://s2.ripple.com:443",
        "server_name": "Ripple-S2",
        "ssl_verify": True,

        "notifications": {
            "twilio": {
                "notify_twilio": False,
                "phone_numbers": [
                    {
                        "phone_from": "+19000000",
                        "phone_to": "+10000000",
                    },
                ],
            },

            "discord": {
                "notify_discord": False,
                "discord_servers": [
                    {
                        "discord_id": "",
                        "discord_token": "",
                    },
                ],
            },

            "mattermost": {
                "notify_mattermost": False,
            },

            "slack": {
                "notify_slack": False,
            },

            "smtp": {
                "notify_smtp": False,
            },
        },
    },


]

############# Validators
# Master keys ('master_key':) typically start with "nH...", rather than
# ephemeral validation keys ('validation_public_key':), which usually begin with "n9...".
# The bot is set will automatically cull duplicate validator entries based on either key type

VALIDATORS = [
    {
        "master_key": "nHU4bLE3EmSqNwfL4AP1UZeTNPrSPPP6FXLKXo2uqfHuvBQxDVKd",
        "server_name": "Ripple.com (master)",
        "notifications": {
            "twilio": {
                "notify_twilio": False,
                "phone_numbers": [
                    {
                        "phone_from": "+19000000",
                        "phone_to": "+10000000",
                    },
                ],
            },

            "discord": {
                "notify_discord": False,
                "discord_servers": [
                    {
                        "discord_id": "",
                        "discord_token": "",
                    },
                ],
            },

            "mattermost": {
                "notify_mattermost": False,
            },

            "slack": {
                "notify_slack": False,
            },

            "smtp": {
                "notify_smtp": False,
            },
        },
    },

    {
        "validation_public_key": "n9Kb81J9kqGgYkrNDRSPT3UCgz8Bei1CPHGMt85yxz9mUSvuzV5k",
        "server_name": "Coil.com (eph)",
        "notifications": {
            "twilio": {
                "notify_twilio": False,
                "phone_numbers": [
                    {
                        "phone_from": "+19000000",
                        "phone_to": "+10000000",
                    },
                ],
            },

            "discord": {
                "notify_discord": False,
                "discord_servers": [
                    {
                        "discord_id": "",
                        "discord_token": "",
                    },
                ],
            },

            "mattermost": {
                "notify_mattermost": False,
            },

            "slack": {
                "notify_slack": False,
            },

            "smtp": {
                "notify_smtp": False,
            },
        },
    },

    {
        "validation_public_key": "n9M2UqXLK25h9YEQTskmCXbWPGhQmB1pFVqeXia38UwLaL838VbG",
        "server_name": "Gatehub.net (eph)",
        "notifications": {
            "twilio": {
                "notify_twilio": False,
                "phone_numbers": [
                    {
                        "phone_from": "+19000000",
                        "phone_to": "+10000000",
                    },
                ],
            },

            "discord": {
                "notify_discord": False,
                "discord_servers": [
                    {
                        "discord_id": "",
                        "discord_token": "",
                    },
                ],
            },

            "mattermost": {
                "notify_mattermost": False,
            },

            "slack": {
                "notify_slack": False,
            },

            "smtp": {
                "notify_smtp": False,
            },
        },
    },
]
