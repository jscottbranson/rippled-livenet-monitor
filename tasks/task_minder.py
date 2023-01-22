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

    logging.info(f"Subscription command will be: {command}")
    return command, val_stream_count

def start_task_loop(settings):
    '''
    Run the asyncio event loop.
    '''
    loop = asyncio.new_event_loop()
    ws_servers = []
    monitor_tasks = []
    val_stream_count = 0
    message_queue = asyncio.Queue(maxsize=999999999)
    notification_queue = asyncio.Queue(maxsize=100000)

    if settings.ASYNCIO_DEBUG is True:
        loop.set_debug(True)
        logging.info("asyncio debugging enabled.")

    while True:
        try:
            logging.info("Adding server subscriptions to the event loop.")
            for server in settings.SERVERS:
                command, val_stream_count = get_command(settings, val_stream_count)
                server['command'] = command
                ws_servers.append(
                    {
                        'task': loop.create_task(
                            websocket_subscribe(
                                server , message_queue
                            )
                        ),
                        'url': server.get('url'),
                        'server_name': server.get('server_name'),
                        'phone_to': server.get('phone_to'),
                        'phone_from': server.get('phone_from'),
                        'command': server.get('command'),
                        'ssl_verify': server.get('ssl_verify'),
                        'retry_count': 0,
                    }
                    )

            monitor_tasks.append(
                loop.create_task(
                    mind_connections(settings, ws_servers, message_queue)
                )
            )

            monitor_tasks.append(
                loop.create_task(
                    ResponseProcessor(settings, message_queue, notification_queue).process_messages()
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
            for server in ws_servers:
                server['task'].cancel()
            for task in monitor_tasks:
                task.cancel()
            logging.critical("Final cleanup asyncio task loop is running.")
            loop.run_forever()
        finally:
            loop.close()
            logging.critical("All asyncio loops have been closed.")
