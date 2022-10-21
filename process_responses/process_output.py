'''
Process messages from the asyncio queue.
'''
import os
import logging
import time
import asyncio

from . import process_stock_output
from . import process_validation_output
from .check_forked import fork_checker

class ResponseProcessor:
    '''
    Process remote server responses to server, ledger, and validation subscription stream messages.

    :param settings: Config file
    :param asyncio.queues.Queue message_queue: Incoming websocket messages
    :param asyncio.queues.Queue sms_queue: Outbound SMS messages
    '''
    def __init__(self, settings, message_queue, sms_queue):
        self.settings = settings
        self.table_stock = {}
        self.table_validator = {}
        self.val_keys = []
        self.processed_validations = []
        self.message_queue = message_queue
        self.sms_queue = sms_queue
        self.time_last_output = 0
        self.time_fork_check = 0


    async def process_console_output(self):
        '''
        Call functions to print messages to the console, depending on settings.

        :param settings: Config file
        '''
        if self.settings.CONSOLE_OUT is True \
           and time.time() - self.time_last_output >= self.settings.CONSOLE_REFRESH_TIME:
            os.system('clear')
            await process_stock_output.print_table_server(self.table_stock)
            if self.settings.VALIDATOR_MASTER_KEYS or self.settings.VALIDATOR_EPH_KEYS:
                await process_validation_output.print_table_validation(self.table_validator)
            self.time_last_output = time.time()

    async def evaluate_forks(self):
        '''
        Call functions to check for forked servers.
        '''
        # this function needs a timer
        if time.time() - self.time_fork_check > self.settings.FORK_CHECK_FREQ:
            table = {}
            table.update(self.table_validator)
            table.update(self.table_stock)
            forks = await fork_checker(self.settings, table, self.sms_queue)
            if forks:
                pass
            self.time_fork_check = time.time()

    async def sort_new_messages(self, message):
        '''
        Check if incoming messages are server, ledger, or validation subscription messages.

        :param dict message: Incoming subscription response
        '''
        # Check for server subscription messages
        if 'result' in message['data']:
            self.table_stock = \
                    await process_stock_output.update_table_server(
                        self.settings, self.table_stock, self.sms_queue, message
                    )

        # Check for ledger subscription messages
        elif message['data']['type'] == 'ledgerClosed':
            self.table_stock = \
                    await process_stock_output.update_table_ledger(
                        self.table_stock, message
                    )

        # Check for validation messages
        elif message['data']['type'] == 'validationReceived':
            self.val_keys, self.table_validator, self.processed_validations = \
                    await process_validation_output.check_validations(
                        self.settings,
                        self.val_keys,
                        self.table_validator,
                        self.processed_validations,
                        message
            )

    async def generate_val_keys(self):
        '''
        Create a list of all potential keys for validators we are monitoring.
        '''
        self.val_keys = list(i['key'] for i in self.settings.VALIDATOR_MASTER_KEYS) \
                + list(i['key'] for i in self.settings.VALIDATOR_EPH_KEYS)

    async def init_variables(self):
        '''
        Create blank tables for stock and validator tracking
        as well as a list of all validator keys to track for.
        '''
        await self.generate_val_keys()
        self.table_stock = await process_stock_output.create_table_stock(self.settings)
        self.table_validator = \
                await process_validation_output.create_table_validation(self.settings)

    async def process_messages(self):
        '''
        Listen for incoming messages and execute functions accordingly.

        '''
        await self.init_variables()

        while True:
            try:
                message = await self.message_queue.get()
                await self.sort_new_messages(message)
                # We don't want to evaluate forks for every new message
                await self.evaluate_forks()
                await self.process_console_output()
            except KeyError as error :
                logging.warning(f"Error: '{error}'. Received an unexpected message: '{message}'.")
            except KeyboardInterrupt:
                logging.info("Keyboard interrupt detected. Response processor stopped.")
                break
