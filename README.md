# rippled Monitor
The purpose of this bot is to provide optional console output and/or remote (SMS, webhooks, SMTP, etc.) messaging output that can be used to notify rippled server operators of issues including state changes and forks.

## How it Works
This bot is designed to subscribe to the `server`, `ledger`, and `validation` streams from multiple rippled servers. It can thus be used to monitor both stock (directly) and validating (indirectly) nodes.

Monitoring can be done by observing the console output and/or subscribing to notifications via Twilio (SMS), Mattermost, Discord, Slack, and/or SMTP.

Specify stock (non-validating) servers you wish to directly connect to via websocket in the `SERVERS` section of `settings.py`.

Specify validating nodes' master or ephemeral validation keys in the appropriate `settings.py` section. Validations from these servers will be sourced from the specified `SERVERS` in `settings.py`.

As this tool is used to monitor the live network, it is not really useful for monitoring reporting mode/Clio servers.

## Warning
This is an early stage project, so expect problems.
This monitoring tool is not intended for solo use in a production environment - please use redundant monitoring for mission-critical infrastructure. No one who contributed to this code is responsible for your servers.

By running this code, you agree the code author(s) are not liable for missed notifications or other issues, including, but not limited to, those arising from errors in the code.

Be cautious when using webhooks, as messages may be lost due to rate limiting or other factors.

## To-Do
1. Attempt to reconnect to servers that stop sending new last_ledger index numbers.
2. Send an admin warning if <= 80% of servers stop advancing.
2. Integrate with sqlite DBs to retrieve server, validator, and notification data.
4. Consider adding an asyncio queue inside the notification_watcher, so that messags can be moved from the blocking multiprocess queue to the asyncio queue for processing without spawning a new thread.
5. Support Slack & email notifications.
6. Notify validator subscribers if their ephemeral key changes.
7. Write a function to scrub sensitive notification data from logging.
8. Account for rippled errors, like tooBusy.

## Notifications
If enabled in `settings.py`, notifications will be sent at the following times:
1. When a server disconnects and/or reconnects
2. When the state for a subscribed server changes
3. When a subscribed server or a monitored validator is more than n ledgers (specified in `settings.py`) ahead of or behind the rest of the network
4. (coming later) When latency is dangerously high between monitoring bot and the remote server
5. Administrators can receive heartbeat messages as specified in `settings.py`
6. (coming later) When a validator changes their amendment votes

At this time, notifications will not be retried if the monitoring server is unable to reach the API. This functionality can be easily integrated in the future by passing the messages back into the notification_queue.

## Running the bot
As written, this code will produce errors with asyncio in Python 3.9. The code is tested and works with 3.10 and 3.11.
1. `git clone https://github.com/jscottbranson/rippled-livenet-monitor.git`
2. `cd rippled-livenet-monitor`
3. `pip install -r requirements.txt`
4. `cp settings_ex.py settings.py`
5. Adjust `settings.py`
6. (optional) Save Twilio notification credentials as env variables.
7. `python3 main.py`

## Generating Configuration Files
The `utils_for_humans` directory contains a `dict_convert.py` script that can be used to assist in generating a configuration file with monitoring output that is consistent across all servers.

## Updating
1. `cd rippled_monitor`
2. ` git pull`
3. This project is early stage, so it's important to check for new settings in `settings_ex.py` after updating.
