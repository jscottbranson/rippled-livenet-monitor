# rippled Monitor
The purpose of this bot is to provide optional console output and/or SMS messaging output that can be used to notify rippled server operators of issues including state changes and forks.

## How it Works
This bot is designed to subscribe to the `server`, `ledger`, and `validation` streams from multiple rippled servers. It can thus be used to monitor both stock (directly) and validating (indirectly) nodes.

Monitoring can be done by observing the console output and/or subscribing to SMS notifications via Twilio (it should be trivial to add functionality for other providers).

Specify stock (non-validating) servers you wish to directly connect to via websocket in the `SERVERS` section of `settings.py`.

Specify validating nodes' master or ephemeral validation keys in the appropriate `settings.py` section. Validations from these servers will be sourced from the specified `SERVERS` in `settings.py`.

As this tool is used to monitor the live network, it is not really useful for monitoring reporting mode/Clio servers.

## Warning
This is an early stage project, so expect problems. For example, asyncio does not clean up neatly when exiting using a keyboard interrupt.
This monitoring tool is not intended for solo use in a production environment - please use redundant monitoring for mission-critical infrastructure.

Be cautious when using webhooks, as messages may be lost due to rate limiting or other factors.

## To-Do
1. Check fields returned by 'server' subscription and update tables accordingly (additional fields are currently logged at the warning level).
2. Attempt to reconnect to servers that stop sending new last_ledger index numbers (and send an admin warning if all servers stop advancing).
3. Integrate with sqlite DBs to retrieve server and contact information mappings.
4. Consider multithreading the websocket connections and output processor.
5. Retry sending messages that fail
6. Support Discord, Slack, Mattermost, and email notifications.

## Notifications
If enabled in `settings.py`, notifications will be sent at the following times:
1. When a server disconnects and/or reconnects
2. When the state for a subscribed server changes
3. When a subscribed server or a monitored validator is more than n ledgers (specified in `settings.py`) ahead of or behind the rest of the network
4. (coming later) When latency is dangerously high between monitoring bot and the remote server
5. Administrators can receive heartbeat messages as specified in `settings.py`

At this time, Twilio notifications will not be retried if the monitoring server is unable to reach the Twilio API. This functionality can be easily integrated in the future by passing the messages back into the notification_queue.

## Running the bot
As written, this code will produce errors with asyncio in Python 3.9. The code is tested and works with 3.10 and 3.11.
1. `git clone https://github.com/crypticrabbit/rippled_monitor.git`
2. `cd rippled_monitor`
3. `pip install -r requirements.txt`
4. `cp settings_ex.py settings.py`
5. Adjust `settings.py` as needed
6. (optional) Save Twilio notification credentials as env variables.
7. `python3 main.py`

## Updating
1. `cd rippled_monitor`
2. ` git pull`
3. This project is early stage, so it's important to check for new settings in `settings_ex.py` after updating.
