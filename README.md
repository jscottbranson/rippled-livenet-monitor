# rippled Monitor
This bot is designed to subscribe to the `server`, `ledger`, and `validation` streams from multiple rippled servers. It can thus be used to monitor both stock (directly) and validating (indirectly) nodes.

Specify stock (non-validating) servers you wish to directly connect to via websocket in the `SERVERS` section of `settings.py`.

Specify validating nodes' master or ephemeral validation keys in the appropriate `settings.py` section. Validations from these servers will be sources from the specified `SERVERS` in `settings.py`.

Console output is available now, text message updates are planned for the future.

This is an early stage project, so expect problems. For example, asyncio does not clean up neatly when exiting using a keyboard interrupt.

## Running the bot
1. `git clone https://github.com/crypticrabbit/rippled_monitor.git`
2. `cd rippled_monitor`
3. `pip install websockets prettytable`
4. `cp settings.py.ex settings.py`
5. Adjust `settings.py` as needed
6. `python3 run.py`
