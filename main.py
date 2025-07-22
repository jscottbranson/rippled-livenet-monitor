'''
Run the program.
'''
import logging
import settings

from sys import exit
from multiprocessing import Process, Queue
import logging

from ws_connection.initialize_ws import start_websocket_loop
from process_responses.process_output import start_output_processing
from notifications.notification_watcher import start_notifications
from misc import generate_tables


def start_bot():
    '''
    Start multiprocessing processes.
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

        except KeyboardInterrupt:
            logging.critical("Keyboard interrupt detected, exiting.")
            logging.critical("Final multiprocessing cleanup is running.")
        finally:
            logging.critical("All threads have been closed.")
            exit(0)

def set_logging():
    '''
    Set logging params.
    '''
    logging.basicConfig(
        filename=settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        format='%(asctime)s %(levelname)s: %(module)s - %(funcName)s (%(lineno)d): %(message)s',
    )

if __name__ == '__main__':
    set_logging()
    start_bot()
