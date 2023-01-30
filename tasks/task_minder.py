'''
Subscribe to the server command on multiple servers, then pass the resultant messages
into a queue for processing.
'''
import logging
import asyncio

from ws_connection.ws_listen import websocket_subscribe
from .ws_minder import mind_connections
from process_responses.process_output import ResponseProcessor
from notifications.notification_watcher import notifications
from misc import generate_tables


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

def start_task_loop(settings):
    '''
    Run the asyncio event loop.
    '''
    loop = asyncio.new_event_loop()
    monitor_tasks = []
    val_stream_count = 0
    message_queue = asyncio.Queue(maxsize=999999999)
    notification_queue = asyncio.Queue(maxsize=100000)

    if settings.ASYNCIO_DEBUG is True:
        loop.set_debug(True)
        logging.info("asyncio debugging enabled.")

    table_stock = generate_tables.create_table_stock(settings)
    table_validator = generate_tables.create_table_validation(settings)

    while True:
        try:
            logging.info("Adding server subscriptions to the event loop.")
            for server in table_stock:
                server['command'], val_stream_count = get_command(settings, val_stream_count)
                server['ws_retry_count'] = 0
                server['ws_connection_task'] = loop.create_task(
                    websocket_subscribe(server, message_queue)
                )

            monitor_tasks.append(
                loop.create_task(
                    mind_connections(settings, table_stock, message_queue)
                )
            )

            monitor_tasks.append(
                loop.create_task(
                    ResponseProcessor(
                        settings, table_stock, table_validator, message_queue, notification_queue
                    ).process_messages()
                )
            )

            monitor_tasks.append(
                loop.create_task(
                    notifications(settings, notification_queue)
                )
            )

            logging.warning("Initial asyncio task list is running.")
            loop.run_forever()

        except (KeyboardInterrupt):
            logging.critical("Keyboard interrupt detected, stopping asyncio loops.")
            for server in table_stock:
                server['ws_connection_task'].cancel()
            for task in monitor_tasks:
                task.cancel()
            logging.critical("Final cleanup asyncio task loop is running.")
            loop.run_forever()
        finally:
            loop.close()
            logging.critical("All asyncio loops have been closed.")
