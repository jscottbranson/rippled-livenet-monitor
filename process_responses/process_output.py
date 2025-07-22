'''
Process messages from the asyncio queue.
'''
import os
import logging
import time
import asyncio

from . import console_output
from .check_forked import fork_checker
from . import process_stock_output
from . import process_validation_output

class ResponseProcessor:
    '''
    Process remote server responses to server, ledger, and validation subscription stream messages.

    :param dict args_d: Default settings, tables, and queues
    '''
    def __init__(self, args_d):
        self.settings = args_d['settings']
        self.table_stock = args_d['table_stock']
        self.table_validator = args_d['table_validator']
        self.forks = []
        self.ll_modes = []
        self.val_keys = []
        self.processed_validations = []
        self.message_queue = args_d['message_queue']
        self.notification_queue = args_d['notification_queue']
        self.time_last_output = 0
        self.time_fork_check = 0
        self.last_heartbeat = time.time()


    async def process_console_output(self):
        '''
        Call functions to print messages to the console, depending on settings.

        :param settings: Config file
        '''
        if self.settings.CONSOLE_OUT is True \
           and time.time() - self.time_last_output >= int(self.settings.CONSOLE_REFRESH_TIME):
            os.system('clear')
            await console_output.print_table_server(self.table_stock)
            if self.table_validator:
                await console_output.print_table_validation(self.table_validator)
                if self.settings.PRINT_AMENDMENTS:
                    await console_output.print_table_amendments(
                        self.table_validator, self.settings.AMENDMENTS
                    )
            self.time_last_output = time.time()

    async def evaluate_forks(self):
        '''
        Call functions to check for forked servers.
        '''
        if time.time() - self.time_fork_check > int(self.settings.FORK_CHECK_FREQ):
            self.ll_modes, self.table_stock, self.table_validator = await fork_checker(
                self.settings, self.table_stock, self.table_validator, self.notification_queue
            )
            self.time_fork_check = time.time()

    async def sort_new_messages(self, message):
        '''
        Check if incoming messages are server, ledger, or validation subscription messages.

        :param dict message: Incoming subscription response
        '''
        # Check for server subscription messages
        if message['data'].get('type') == 'serverStatus' or message['data'].get('result'):
            self.table_stock = \
                    await process_stock_output.update_table_server(
                        self.table_stock, self.notification_queue, message
                    )

        # Check for ledger subscription messages
        elif message['data'].get('type') == 'ledgerClosed':
            self.table_stock = \
                    await process_stock_output.update_table_ledger(
                        self.table_stock, message
                    )

        # Check for validation messages
        elif message['data'].get('type') == 'validationReceived':
            self.val_keys, self.table_validator, self.processed_validations = \
                    await process_validation_output.check_validations(
                        self.settings,
                        self.val_keys,
                        self.table_validator,
                        self.processed_validations,
                        message
            )

        else:
            logging.warning("Message received that couldn't be sorted: '%s'.", message)

    async def generate_val_keys(self):
        '''
        Create a list of all potential keys for validators we are monitoring.
        '''
        val_keys = list(i.get('master_key') for i in self.table_validator) \
                + list(i.get('validation_public_key') for i in self.table_validator)

        for i in val_keys:
            if i:
                self.val_keys.append(i)
        logging.warning(
            "Created initial validation key tracking list with: '%d' items.", len(self.val_keys)
        )

    async def heartbeat_message(self):
        '''
        Send an SMS message periodically.
        '''
        if self.settings.ADMIN_HEARTBEAT \
           and time.time() - self.last_heartbeat >= int(self.settings.HEARTBEAT_INTERVAL):
            now = time.strftime("%m-%d %H:%M:%S", time.gmtime())
            message = "Livenet Monitoring Bot heartbeat. "
            message = message + str(f"LL mode: '{self.ll_modes[0]}'. ")
            message = message + str(f"Server time (UTC): '{now}'.")
            logging.info(message)

            for admin in self.settings.ADMIN_NOTIFICATIONS:
                self.notification_queue.put(
                    {
                        'message': message,
                        'server': admin,
                    }
                )

            self.last_heartbeat = time.time()

    async def process_messages(self):
        '''
        Listen for incoming messages and execute functions accordingly.

        '''
        await self.generate_val_keys()

        while True:
            try:
                message = self.message_queue.get()
                await self.sort_new_messages(message)
                await self.evaluate_forks()
                await self.process_console_output()
                await self.heartbeat_message()
            except KeyError as error :
                logging.warning(
                    "Error: '%s'. Received an unexpected message: '%s'.", error, message
                )
            except (asyncio.CancelledError, KeyboardInterrupt):
                logging.critical("Keyboard interrupt detected. Response processor stopped.")
                break
            except Exception as error:
                logging.critical("Otherwise uncaught exception in response processor: '%s'.", error)

def start_output_processing(args_d):
    '''
    Start the asyncio loop.

    :param dict args_d: Default settings, queues, and tables.
    '''
    loop = asyncio.new_event_loop()
    monitor_tasks = []

    try:
        monitor_tasks.append(
            loop.create_task(ResponseProcessor(args_d).process_messages())
        )

        logging.warning("Response processor loop started.")
        loop.run_forever()

    except KeyboardInterrupt:
        for task in monitor_tasks:
            task.cancel()
        logging.critical("Closed response processor asyncio loops.")
