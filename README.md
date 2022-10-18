# rippled Monitor
The purpose of this bot is to provide optional console output and/or SMS messaging output that can be used to notify rippled server operators of issues including state changes and forks.

## How it Works
This bot is designed to subscribe to the `server`, `ledger`, and `validation` streams from multiple rippled servers. It can thus be used to monitor both stock (directly) and validating (indirectly) nodes.

Monitoring can be done by observing the console output and/or subscribing to SMS notifications via Twilio (it should be trivial to add functionality for other providers).

Specify stock (non-validating) servers you wish to directly connect to via websocket in the `SERVERS` section of `settings.py`.

Specify validating nodes' master or ephemeral validation keys in the appropriate `settings.py` section. Validations from these servers will be sourced from the specified `SERVERS` in `settings.py`.

As this tool is used to monitor the live network, it is not particularly useful for monitoring reporting mode servers.

## Warning
This is an early stage project, so expect problems. For example, asyncio does not clean up neatly when exiting using a keyboard interrupt. All commits have been made to main - there is no development branch at this point - so consider everything potentially unstable. This monitoring tool is not yet intended for use in production environments (however, it does tend to be pretty stable).

## Twilio Notifications
If enabled in `settings.py`, Twilio notifications will be sent at the following times:
1. Any server disconnect and again on reconnect
2. When the state for a subscribed server changes
3. (coming soon) when a subscribed server or a monitored validator are more than n ledgers ahead or behind the rest of the network
4. (coming later) when latency is dangerously high between monitoring bot and the remote server

At this time, Twilio notifications will not be retried if the monitoring server is unable to reach the Twilio API. This functionality can be easily integrated in the future.

## Running the bot
1. `git clone https://github.com/crypticrabbit/rippled_monitor.git`
2. `cd rippled_monitor`
3. `pip install websockets prettytable twilio`
4. `cp settings.py.ex settings.py`
5. Adjust `settings.py` as needed
6. (optional) Save Twilio credentials as env variables.
7. `python3 main.py`

## Updating
1. `cd rippled_monitor`
2. ` git pull`
3. This project is early stage, so it's important to check for new settings in `settings.py.ex` after updating.
