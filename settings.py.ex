'''
This file is used to configure the monitoring bot.
'''
import logging

LOG_FILE = "monitor.log" # Where should the log file live?

LOG_LEVEL = logging.WARNING # How verbose should the logs be ("INFO", "WARNING", "ERROR", "CRITICAL")?

# An array with each server IP address mapped to a human readable address.
# These should be stock servers (validators typically should not allow inbound connections).
# As the number of servers in this array increases (up to MAX_VAL_STREAMS),
# the probability of a false missed validation from a below validator decreases
# (in other words, validation monitoring gets more accurate with more stock servers).
SERVERS = [
    {"url": "wss://xrplcluster.com:443", "name": "Cluster", "ssl_verify": True, "phone_from": "+19000000", "phone_to": "+10000000"},
    {"url": "wss://s1.ripple.com:443", "name": "Ripple-S1", "ssl_verify": True, "phone_from": "+19000000", "phone_to": "+10000000"},
    {"url": "wss://s2.ripple.com:443", "name": "Ripple-S2", "ssl_verify": True, "phone_from": "+19000000", "phone_to": "+10000000"},
]

# A list of dicts with validation public keys to monitor for missed validations
# Master keys typically start with "nH...", rather than ephemeral validation keys,
# which usually begin with "n9...".
# Keys should be included in either the master or eph keys list, not both
# (although inclusion of one server in both lists shouldn't produce duplicate
# results).
VALIDATOR_MASTER_KEYS = [
    {"key": "nHDwHQGjKTz6R6pFigSSrNBrhNYyUGFPHA75HiTccTCQzuu9d7Za", "name": "Coil.com (master)", "phone_from": "+19000000", "phone_to": "+10000000"},
    {"key": "nHU4bLE3EmSqNwfL4AP1UZeTNPrSPPP6FXLKXo2uqfHuvBQxDVKd", "name": "Ripple.com (master)"}, "phone_from": "+19000000", "phone_to": "+10000000"},
]

VALIDATOR_EPH_KEYS = [
    {"key": "n9Kb81J9kqGgYkrNDRSPT3UCgz8Bei1CPHGMt85yxz9mUSvuzV5k", "name": "Coil.com (eph)", "phone_from": "+19000000", "phone_to": "+10000000"},
    {"key": "n9M2UqXLK25h9YEQTskmCXbWPGhQmB1pFVqeXia38UwLaL838VbG", "name": "Gatehub.net (eph)", "phone_from": "+19000000", "phone_to": "+10000000"},
]

WS_RETRY = 20 # number of seconds to wait between dropped WS connection checks

REMOVE_DUP_VALIDATORS = True # Allow the same validator master/eph keys to be tracked more than once
# This should be 'False' if alerts will be sent to multiple phone numbers for the same validator.


PROCESSED_VAL_MAX = 10000 # Maximum number of validation messages to store to avoid duplicates
# when this number is reached, half of the validation message tracking list will be deleted.

MAX_CONNECT_ATTEMPTS = 999999 # Max number of connection retries

MAX_VAL_STREAMS = 5 # Max validations streams to subscribe to. These produce a lot of messages.
# Client too slow WS disconnects, seemingly forked servers, and other unexpected behavior can result from excessive validation stream subscriptions.
# Too few streams can result in false missed validation messages.
# The above setting is ignored if no validators are defined for monitoring.

LL_FORK_CUTOFF = 25 # Number of ledgers ahead of or behind the mode of
# the servers being monitored to consider a server forked

FORK_CHECK_FREQ = 10 # Number of seconds to wait between checks for forked servers

ASYNCIO_DEBUG = False # Verbose logging from asyncio

#### Console Output ####
CONSOLE_OUT = True # Print a fancy table to the console

CONSOLE_REFRESH_TIME = 5 # Time in seconds to wait before refreshing console output.

#### SMS Settings ####
SMS = False # Should we send SMS notifications?

TWILIO = False # Should notifications be sent via Twilio?
# If TWILIO_ACCOUNT_SID and/or TWILIO_AUTH_TOKEN below are set to "None",
# they will be sourced from env variables of the same name (this is likely more secure).
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None

# Numbers should be prefixed with a "+" and the country code (e.g., +1 for the USA).
NUMBER_FROM = "+12223333"
NUMBER_TO = "+12223333"
