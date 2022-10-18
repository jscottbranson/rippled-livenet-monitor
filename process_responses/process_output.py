'''
Process messages from the asyncio queue.
'''
import os
import logging
import time
import asyncio

from . import process_stock_output
from . import process_validation_output

async def process_messages(settings, message_queue, sms_queue):
    '''
    Do stuff with messages.

    :param settings: Config file
    :param asyncio.queues.Queue message_queue: Incoming websocket messages
    :param asyncio.queues.Queue sms_queue: Outbound SMS messages
    '''
    time_last_output = 0

    # Create a blank template table with the servers we will monitor.
    table_stock = await process_stock_output.create_table_stock(settings)
    logging.info("Initial blank server table created.")

    # Create lists of validation keys to monitor for
    table_validator = await process_validation_output.create_table_validation(settings)
    val_keys = list(i['key'] for i in settings.VALIDATOR_MASTER_KEYS) \
            + list(i['key'] for i in settings.VALIDATOR_EPH_KEYS)
    processed_validations = []
    # NOTE TO SELF: Don't forget to clean the processed_validations queue

    while True:
        try:
            message = await message_queue.get()
            # Check for server subscription messages
            if 'result' in message['data']:
                logging.info(f"Server status message received from '{message['server_url']}'. Preparing to update the table.")
                table_stock = await process_stock_output.update_table_server(settings, table_stock, message, sms_queue)
                logging.info(f"Successfully updated the table with server status message from: '{message['server_url']}'.")
            # Check for ledger subscription messages
            elif message['data']['type'] == 'ledgerClosed':
                logging.info(f"New ledger closed message from '{message['server_url']}'.")
                table_stock = await process_stock_output.update_table_ledger(table_stock, message)
                logging.info(f"Successfully updated the table with ledger closed message from: '{message['server_url']}'.")
            # Check for validation messages
            elif message['data']['type'] == 'validationReceived':
                logging.info(f"New validation message from '{message['server_url']}'.")
                val_keys, table_validator, processed_validations = await process_validation_output.check_validations(
                    settings, val_keys, table_validator, processed_validations, message
                )

            if settings.CONSOLE_OUT is True and time.time() - time_last_output >= settings.CONSOLE_REFRESH_TIME:
                os.system('clear')
                logging.info("Preparing to print updated server table.")
                await process_stock_output.print_table_server(table_stock)
                logging.info("Successfully printed updated server table.")

                if settings.VALIDATOR_MASTER_KEYS or settings.VALIDATOR_EPH_KEYS:
                    logging.info("Preparing to print updated validations table.")
                    await process_validation_output.print_table_validation(table_validator)
                    logging.info("Successfully printed updated validations table.")
                time_last_output = time.time()
        except KeyError as error :
            logging.warning(f"Error: '{error}'. Received an unexpected message: '{message}'.")
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Processor is stopping listening for messages.")
            break
