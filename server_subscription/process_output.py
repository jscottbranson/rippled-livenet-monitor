'''
Process messages from the asyncio queue.
'''
import os
import logging
import time
import asyncio

from prettytable import PrettyTable

async def format_table(table):
    '''
    Format values to human readable.
    '''
    color_reset = "\033[0;0m"
    green = "\033[0;32m"
    red = "\033[1;31m"
    for key in table:
        if isinstance(table[key]['ledger_hash'], str):
            table[key]['ledger_hash'] = table[key]['ledger_hash'][:5]
        if isinstance(table[key]['server_status'], str):
            if table[key]['server_status'] == "full":
                table[key]['server_status'] = green + table[key]['server_status'] + color_reset
            else:
                table[key]['server_status'] = red + table[key]['server_status'] + color_reset

    return table

async def print_table(table):
    '''
    Print a pretty table to the console.
    '''
    pretty_table = PrettyTable()
    pretty_table.field_names = [
        "Server Name", "State", "Base Load", "Srv Load",
        "Net Load", "Base Fee", "Ref Fee", "Fee Escalation",
        "Queue Fee", "LL Index", "LL Hash", "LL # Tx", "Time Last Update"
    ]
    table = await format_table(table)
    for key in table:
        pretty_table.add_row([
            table[key]['server_name'],
            table[key]['server_status'],
            table[key]['load_base'],
            table[key]['load_factor_server'],
            table[key]['load_factor'],
            table[key]['fee_base'],
            table[key]['fee_ref'],
            table[key]['load_factor_fee_escalation'],
            table[key]['load_factor_fee_queue'],
            table[key]['ledger_index'],
            table[key]['ledger_hash'],
            table[key]['txn_count'],
            table[key]['time_updated'],
            ])
    os.system('clear')
    print(pretty_table)

async def update_table_ledger(table, message):
    '''
    Add information from ledger closed messages into the table.
    '''
    update = table[message['server_url']]

    update['ledger_index'] = message['data'].get('ledger_index')
    update['ledger_hash'] = message['data'].get('ledger_hash')
    update['txn_count'] = message['data'].get('txn_count')

    return table

async def update_table_server(table, message):
    '''
    Add info contained in new messages to the table.
    '''
    update = table[message['server_url']]
    message = message['data']['result']

    update['fee_base'] = message.get('fee_base')
    update['fee_ref'] = message.get('fee_ref')
    update['load_base'] = message.get('load_base')
    update['load_factor'] = message.get('load_factor')
    update['load_factor_fee_escalation'] = message.get('load_factor_fee_escalation')
    update['load_factor_fee_queue'] = message.get('load_factor_fee_queue')
    update['load_factor_fee_reference'] = message.get('load_factor_fee_reference')
    update['load_factor_fee_server'] = message.get('load_factor_fee_server')
    update['server_status'] = message.get('server_status')
    update['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

    return table

async def create_table(settings):
    '''
    Create a table representing each server in the settings file.
    '''
    table = {}
    for server in settings.SERVERS:
        table[server['url']] = {
            'server_name': server['name'],
            'fee_base': None,
            'fee_ref': None,
            'load_base': None,
            'reserve_base': None,
            'reserve_inc': None,
            'load_factor': None,
            'load_factor_fee_escalation': None,
            'load_factor_fee_queue': None,
            'load_factor_fee_reference': None,
            'load_factor_server': None,
            'server_status': None,
            'ledger_index': None,
            'ledger_hash': None,
            'txn_count': None,
            'time_updated': None,
        }
    return table

async def process_messages(settings, message_queue):
    '''
    Do stuff with messages.
    '''
    # Create a blank template table with the servers we will monitor.
    table = await create_table(settings)
    logging.info("Initial blank table created.")
    while True:
        message = await message_queue.get()
        try:
            if 'result' in message['data']:
                logging.info(f"Server status message received from {message['server_url']}. Preparing to update the table.")
                table = await update_table_server(table, message)
                logging.info(f"Successfully updated the table with server status message from: {message['server_url']}.")
            elif message['data']['type'] == 'ledgerClosed':
                logging.info(f"New ledger closed message from {message['server_url']}.")
                table = await update_table_ledger(table, message)
            if settings.CONSOLE_OUT is True:
                logging.info(f"Preparing to print updated table based on message from: {message['server_url']}.")
                await print_table(table)
                logging.info(f"Successfully printed updated table based on message from: {message['server_url']}.")
        except KeyError:
            logging.warning(f"Received an unexpected message: {message}.")
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Processor is stopping listening for messages.")
            break
