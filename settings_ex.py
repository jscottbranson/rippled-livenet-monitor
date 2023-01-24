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

#### Random ####
REMOVE_DUP_VALIDATORS = True # Allow the same validator master/eph keys to be tracked more than once

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
            },

            "slack": {
                "notify_slack": False,
            },

            "email": {
                "notify_email": False,
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

            "email": {
                "notify_email": False,
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

            "email": {
                "notify_email": False,
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

            "email": {
                "notify_email": False,
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
        "master_key": "nHDwHQGjKTz6R6pFigSSrNBrhNYyUGFPHA75HiTccTCQzuu9d7Za",
        "server_name": "Coil.com (master)",
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

            "email": {
                "notify_email": False,
            },
        },
    },

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

            "email": {
                "notify_email": False,
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

            "email": {
                "notify_email": False,
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

            "email": {
                "notify_email": False,
            },
        },
    },
]
