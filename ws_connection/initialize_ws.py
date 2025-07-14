'''
Subscribe to the server command on multiple servers, then pass the resultant messages
into a queue for processing.
'''
import logging
import asyncio

from .ws_listen import websocket_subscribe
from .ws_minder import mind_connections


def get_command(settings, val_stream_count):
    '''
    Only subscribe to the validation stream if necessary.
    '''
    if not settings.VALIDATORS:
        command = {"command": "subscribe", "streams": ["server", "ledger"], "ledger_index": "current"}
    elif val_stream_count >= settings.MAX_VAL_STREAMS:
        command = {"command": "subscribe", "streams": ["server", "ledger"], "ledger_index": "current"}
    else:
        command = {"command": "subscribe", "streams": ["server", "ledger", "validations"], "ledger_index": "current"}
        val_stream_count += 1

    return command, val_stream_count

def start_websocket_loop(args_d):
    '''
    Create an asyncio event loop then subscribe to websocket connections and pass the connections to the reconnection minder.

    :param dict args_d: Settings, etc.
    '''
    loop = asyncio.new_event_loop()
    val_stream_count = 0
    monitor_tasks = []

    if args_d['settings'].ASYNCIO_DEBUG is True:
        loop.set_debug(True)
        logging.info("asyncio debugging enabled.")

    logging.info("Adding server subscriptions to the event loop.")
    for server in args_d['table_stock']:
        server['command'], val_stream_count = get_command(args_d['settings'], val_stream_count)
        server['ws_retry_count'] = 0
        server['ws_connection_task'] = loop.create_task(
            websocket_subscribe(server, args_d['message_queue'])
        )

    monitor_tasks.append(
        loop.create_task(
            mind_connections(
                args_d['settings'],
                args_d['table_stock'],
                args_d['message_queue']
            )
        )
    )

    logging.warning("Initial websocket asyncio task list is running.")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.critical("Keyboard interrupt detected, exiting.")
        for server in args_d['table_stock']:
            server['ws_connection_task'].cancel()
        for task in monitor_tasks:
            task.cancel()
    finally:
        logging.critical("Final cleanup asyncio task loop is running.")
        loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        logging.critical("All websocket asyncio loops have been closed.")
