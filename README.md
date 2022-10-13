# rippled Monitor
This bot is designed to subscribe to the `server`, `ledger`, and `validation` streams from multiple rippled servers. It can thus be used to monitor both stock (directly) and validating (indirectly) nodes.

Monitoring can be done by observing the console output and/or subscribing to SMS notifications via Twilio (it should be trivial to add functionality for other providers).

Specify stock (non-validating) servers you wish to directly connect to via websocket in the `SERVERS` section of `settings.py`.

Specify validating nodes' master or ephemeral validation keys in the appropriate `settings.py` section. Validations from these servers will be sourced from the specified `SERVERS` in `settings.py`.

As this tool is used to monitor the live network, it is not particularly useful for monitoring reporting mode servers.

This is an early stage project, so expect problems. For example, asyncio does not clean up neatly when exiting using a keyboard interrupt. Similarly, "State" should be updated when a server is disconnected.

## Twilio Notifications
If enabled in `settings.py`, Twilio notifications will be sent at the following times:
1. Any server disconnect and again on reconnect
2. When the state for a subscribed server changes
3. (coming soon) when a subscribed server or a monitored validator are more than n ledgers ahead or behind the rest of the network

## Running the bot
1. `git clone https://github.com/crypticrabbit/rippled_monitor.git`
2. `cd rippled_monitor`
3. `pip install websockets prettytable twilio`
4. `cp settings.py.ex settings.py`
5. Adjust `settings.py` as needed
6. (optional) Save Twilio credentials as env variables.
7. `python3 run.py`

## Updating
1. `cd rippled_monitor`
2. ` git pull`
3. This project is early stage, so it's important to check for new settings in `settings.py.ex` after updating.
