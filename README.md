# rippled Monitor
This bot is designed to subscribe to the `server` and `ledger` streams from multiple rippled servers.

Console output is available now, text message updates are planned for the future.

This is an early stage project, so expect problems. For example, asyncio does not clean up neatly when exiting using a keyboard interrupt.

## Running the bot
1. Clone the repo
2. pip install websockets prettytable
3. `cp settings.py.ex settings.py`
4. Adjust settings.py as needed
5. python3 run.py
