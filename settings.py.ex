'''
This file is used to configure the monitoring bot.
'''

LOG_FILE = "info.log" # Where should the log file live?

# An array with each server IP address mapped to a human readable address.
SERVERS = [
    {"url": "wss://s1.ripple.com:443", "name": "Ripple-S1", "ssl_verify": True},
    {"url": "wss://s2.ripple.com:443", "name": "Ripple-S2", "ssl_verify": True},
]

WS_RETRY = 20 # number of seconds to wait between dropped WS connection checks

MAX_CONNECT_ATTEMPTS = 999999 # Max number of connection retries

CONSOLE_OUT = True # Print a fancy table to the console

CONSOLE_REFRESH_TIME = 5 # Time in seconds to wait before refreshing console output.

ASYNCIO_DEBUG = False # Verbose logging from asyncio
