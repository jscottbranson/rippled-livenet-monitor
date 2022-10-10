'''
This file is used to configure the monitoring bot.
'''

LOG_FILE = "info.log" # Where should the log file live?

# An array with each server IP address mapped to a human readable address.
# These should be stock servers (validators typically should not allow inbound connections).
# As the number of servers in this array increases, the probability of a false missed validation
# from a below validator decreases (in other words, validation monitoring gets more accurate
# with more stock servers).
SERVERS = [
    {"url": "wss://s1.ripple.com:443", "name": "Ripple-S1", "ssl_verify": True},
    {"url": "wss://s2.ripple.com:443", "name": "Ripple-S2", "ssl_verify": True},
]

# A list of dicts with validation public keys to monitor for missed validations
# Master keys typically start with "nH...", rather than ephemeral validation keys,
# which usually begin with "n9...".
# Keys should be included in either the master or eph keys list, not both
# (although inclusion of one server in both lists shouldn't produce duplicate
# results).
VALIDATOR_MASTER_KEYS = [
    {"key": "nHDwHQGjKTz6R6pFigSSrNBrhNYyUGFPHA75HiTccTCQzuu9d7Za", "name": "Coil.com (master)"},
    {"key": "nHU4bLE3EmSqNwfL4AP1UZeTNPrSPPP6FXLKXo2uqfHuvBQxDVKd", "name": "Ripple.com (master)"},
]

VALIDATOR_EPH_KEYS = [
    {"key": "n9Kb81J9kqGgYkrNDRSPT3UCgz8Bei1CPHGMt85yxz9mUSvuzV5k", "name": "Coil.com (eph)"},
    {"key": "n9M2UqXLK25h9YEQTskmCXbWPGhQmB1pFVqeXia38UwLaL838VbG", "name": "Gatehub.net (eph)"},
]

PROCESSED_VAL_MAX = 10000 # Maximum number of validation messages to store to avoid duplicates
# when this number is reached, half of the validation message tracking list will be deleted.

WS_RETRY = 20 # number of seconds to wait between dropped WS connection checks

MAX_CONNECT_ATTEMPTS = 999999 # Max number of connection retries

CONSOLE_OUT = True # Print a fancy table to the console

CONSOLE_REFRESH_TIME = 5 # Time in seconds to wait before refreshing console output.

ASYNCIO_DEBUG = False # Verbose logging from asyncio
