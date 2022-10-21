'''
Subscribe to the server command on multiple servers, then pass the resultant messages
into a queue for processing.
'''
import logging
import asyncio

from ws_connection.ws_listen import websocket_subscribe
from .ws_minder import mind_tasks
from process_responses import process_output
from notifications.notification_watcher import notifications


async def get_command(settings, val_stream_count):
    '''
    Only subscribe to the validation stream if necessary.
    '''
    if not settings.VALIDATOR_MASTER_KEYS and not settings.VALIDATOR_EPH_KEYS:
        command = {"command": "subscribe", "streams": ["server", "ledger"], "ledger_index": "current"}
    elif val_stream_count >= settings.MAX_VAL_STREAMS:
        command = {"command": "subscribe", "streams": ["server", "ledger"], "ledger_index": "current"}
    else:
        command = {"command": "subscribe", "streams": ["server", "ledger", "validations"], "ledger_index": "current"}
        val_stream_count += 1

    logging.info(f"Subscription command will be: {command}")
    return command, val_stream_count

async def spawn_connections(settings):
    '''
    Add connections into the asyncio loop.
    '''
    ws_servers = []
    val_stream_count = 0
    message_queue = asyncio.Queue(maxsize=0)
    sms_queue = asyncio.Queue(maxsize=0)
    logging.info("Adding server subscriptions to the event loop.")

    for server in settings.SERVERS:
        command, val_stream_count = await get_command(settings, val_stream_count)
        server['command'] = command
        ws_servers.append(
            {
                'task': asyncio.ensure_future(
                    websocket_subscribe(
                        server , message_queue
                    )
                ),
                'url': server['url'],
                'name': server['name'],
                'command': command,
                'ssl_verify': server['ssl_verify'],
                'retry_count': 0,
            }
            )

    asyncio.ensure_future(
        mind_tasks(settings, ws_servers, message_queue)
    )
    asyncio.ensure_future(
        #process_messages(settings, message_queue, sms_queue)
        process_output.ResponseProcessor(settings, message_queue, sms_queue).process_messages()
    )
    asyncio.ensure_future(
        notifications(settings, sms_queue)
    )

    logging.warning("Initial asyncio task list is running.")

def start_task_loop(settings):
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
        except (
            KeyboardInterrupt,
        ):
            logging.critical("Keyboard interrupt detected, stopping asyncio loops.")
            loop._default_executor.shutdown(wait=True)
            loop.close()
            logging.critical("asyncio loops have been closed.")
