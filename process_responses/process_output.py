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
        self.forks = []
        self.val_keys = []
        self.processed_validations = []
        self.message_queue = message_queue
        self.sms_queue = sms_queue
        self.time_last_output = 0
        self.time_fork_check = 0
        self.last_heartbeat = time.time()


    async def process_console_output(self):
        '''
        Call functions to print messages to the console, depending on settings.

        :param settings: Config file
        '''
        if self.settings.CONSOLE_OUT is True \
           and time.time() - self.time_last_output >= self.settings.CONSOLE_REFRESH_TIME:
            os.system('clear')
            await process_stock_output.print_table_server(self.table_stock)
            if self.table_validator:
                await process_validation_output.print_table_validation(self.table_validator)
            self.time_last_output = time.time()

    async def evaluate_forks(self):
        '''
        Call functions to check for forked servers.
        '''
        if time.time() - self.time_fork_check > self.settings.FORK_CHECK_FREQ:
            table = self.table_validator + self.table_stock
            self.forks = await fork_checker(self.settings, table, self.sms_queue, self.forks)
            forked_names = []
            for fork in self.forks:
                forked_names.append(fork['server_name'])
            for server in self.table_stock + self.table_validator:
                if server['server_name'] in forked_names:
                    server['forked'] = True
                else:
                    server['forked'] = False

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
        logging.info(f"Created initial validation key tracking list with: '{len(self.val_keys)}' items.")

    async def init_variables(self):
        '''
        Create blank tables for stock and validator tracking
        as well as a list of all validator keys to track for.
        '''
        await self.generate_val_keys()
        self.table_stock = await process_stock_output.create_table_stock(self.settings)
        self.table_validator = \
                await process_validation_output.create_table_validation(self.settings)
        logging.info("Initial stock & validator tables created. Ready to process server responses.")

    async def heartbeat_message(self):
        '''
        Send an SMS message periodically.
        '''
        if self.settings.ADMIN_HEARTBEAT and self.settings.SMS:
            if time.time() - self.last_heartbeat >= self.settings.HEARTBEAT_INTERVAL:
                now = time.strftime("%m-%d %H:%M:%S", time.gmtime())
                message = str(f"rippled Livenet Monitor bot heartbeat. Server time: {now}.")
                logging.warning(message)
                await self.sms_queue.put(
                    {
                        'message': message,
                        'phone_from': self.settings.ADMIN_PHONE_FROM,
                        'phone_to': self.settings.ADMIN_PHONE_TO,
                    }
                )
                self.last_heartbeat = time.time()

    async def process_messages(self):
        '''
        Listen for incoming messages and execute functions accordingly.

        '''
        await self.init_variables()

        while True:
            try:
                message = await self.message_queue.get()
                await self.sort_new_messages(message)
                await self.evaluate_forks()
                await self.process_console_output()
                await self.heartbeat_message()
            except KeyError as error :
                logging.warning(f"Error: '{error}'. Received an unexpected message: '{message}'.")
            except (asyncio.CancelledError, KeyboardInterrupt):
                logging.critical("Keyboard interrupt detected. Response processor stopped.")
                break
            except Exception as error:
                logging.critical(f"Otherwise uncaught exception in response processor: '{error}'.")
