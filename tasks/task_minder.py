'''
Subscribe to the server command on multiple servers, then pass the resultant messages
into a queue for processing.
'''
from sys import exit
from multiprocessing import Process, Queue
import logging
import asyncio

from ws_connection.initialize_ws import start_websocket_loop
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

def start_notifications(args_d):
    '''
    Start the notification dispatcher.
    '''
    loop = asyncio.new_event_loop()
    monitor_tasks = []

    try:
        monitor_tasks.append(
            loop.create_task(
                notifications(args_d['settings'], args_d['notification_queue'])
            )
        )

        logging.warning("Notification loop started.")
        loop.run_forever()

    except KeyboardInterrupt:
        for task in monitor_tasks:
            task.cancel()
        logging.critical("Closed notification loops.")

def start_output_processing(args_d):
    '''
    Start processing websocket responses.
    '''
    loop = asyncio.new_event_loop()
    monitor_tasks = []

    try:
        monitor_tasks.append(
            loop.create_task(
                ResponseProcessor(
                    args_d['settings'],
                    args_d['table_stock'],
                    args_d['table_validator'],
                    args_d['message_queue'],
                    args_d['notification_queue']
                ).process_messages()
            )
        )

        logging.warning("Response processor loop started.")
        loop.run_forever()

    except KeyboardInterrupt:
        for task in monitor_tasks:
            task.cancel()
        logging.critical("Closed output processing loops.")

def start_task_loop(settings):
    '''
    Run the asyncio event loop.
    '''
    processes = []
    message_queue = Queue()
    notification_queue = Queue()

    table_stock = generate_tables.create_table_stock(settings)
    table_validator = generate_tables.create_table_validation(settings)

    args_d = {
        'settings': settings,
        'table_stock': table_stock,
        'table_validator': table_validator,
        'message_queue': message_queue,
        'notification_queue': notification_queue,
    }

    processes.append(Process(target=start_websocket_loop, args=(args_d,)))
    processes.append(Process(target=start_output_processing, args=(args_d,)))
    processes.append(Process(target=start_notifications, args=(args_d,)))

    while True:
        try:
            for process in processes:
                process.start()
            for process in processes:
                process.join()
            logging.warning("Initial multiprocessing list is running.")

        except (KeyboardInterrupt):
            logging.critical("Keyboard interrupt detected, exiting.")
            logging.critical("Final multiprocessing cleanup is running.")
        finally:
            logging.critical("All threads have been closed.")
            exit(0)
