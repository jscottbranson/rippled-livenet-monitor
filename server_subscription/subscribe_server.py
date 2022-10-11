'''
Subscribe to the server command on multiple servers, then pass the resultant messages
into a queue for processing.
'''
import logging
import asyncio

from ws_connection.ws_listen import websocket_subscribe
from ws_connection.ws_minder import mind_tasks
from .process_output import process_messages


async def get_command(settings):
    '''
    Only subscribe to the validation stream if necessary.
    '''
    if not settings.VALIDATOR_MASTER_KEYS and not settings.VALIDATOR_EPH_KEYS:
        command = {"command": "subscribe", "streams": ["server", "ledger"], "ledger_index": "current"}
    else:
        command = {"command": "subscribe", "streams": ["server", "ledger", "validations"], "ledger_index": "current"}

    logging.info(f"Subscription command will be: {command}")
    return command

async def spawn_connections(settings):
    '''
    Add connections into the asyncio loop.
    '''
    ws_servers = []
    message_queue = asyncio.Queue(maxsize=0)
    command = await get_command(settings)
    logging.info("Adding server subscriptions to the event loop.")
    for server in settings.SERVERS:
        ws_servers.append(
            {
                'task': asyncio.ensure_future(
                    websocket_subscribe(
                        server , command, message_queue
                    )
                ),
                'url': server['url'],
                'name': server['name'],
                'ssl_verify': server['ssl_verify'],
                'retry_count': 0,
            }
            )

    asyncio.ensure_future(
        process_messages(settings, message_queue)
    )

    asyncio.ensure_future(
        mind_tasks(settings, ws_servers, command, message_queue)
    )
    logging.warning("Initial asyncio task list is running.")

def start_server_info(settings):
    '''
    Run the asyncio event loop.
    '''
    loop = asyncio.new_event_loop()
    if settings.ASYNCIO_DEBUG is True:
        loop.set_debug(True)
        logging.info("asyncio debugging enabled.")

    while True:
        try:
            loop.run_until_complete(spawn_connections(settings))
            loop.run_forever()
        except KeyboardInterrupt:
            logging.critical("Keyboard interrupt detected, stopping asyncio loops.")
            break
