'''
Process server and ledger subscription messages.
This output is not relevant for monitoring validations.
'''
import logging
import time
import asyncio
from copy import deepcopy

from prettytable import PrettyTable

async def format_table_server(table):
    '''
    Format values to human readable.

    :param list table: Dictionary for each server being tracked
    :rtype: list
    '''
    color_reset = "\033[0;0m"
    green = "\033[0;32m"
    red = "\033[1;31m"
    for server in table:
        if isinstance(server['ledger_hash'], str):
            server['ledger_hash'] = server['ledger_hash'][:5]
        if isinstance(server['server_status'], str):
            if server['server_status'] == "full":
                server['server_status'] = green + server['server_status'] + color_reset
            else:
                server['server_status'] = red + server['server_status'] + color_reset

    return table

async def print_table_server(table):
    '''
    Print a pretty table to the console.

    :param list table: Dictionary for each server being tracked
    '''
    logging.info("Preparing to print updated server table.")
    pretty_table = PrettyTable()
    pretty_table.field_names = [
        "Server Name", "State", "Base Load", "Srv Load",
        "Net Load", "Base Fee", "Ref Fee", "Fee Escalation",
        "Queue Fee", "History", "LL Hash", "LL Index", "LL # Tx", "Last Updated"
    ]
    table_new = await format_table_server(deepcopy(table))
    for server in table_new:
        pretty_table.add_row([
            server['server_name'],
            server['server_status'],
            server['load_base'],
            server['load_factor_server'],
            server['load_factor'],
            server['fee_base'],
            server['fee_ref'],
            server['load_factor_fee_escalation'],
            server['load_factor_fee_queue'],
            server['validated_ledgers'],
            server['ledger_hash'],
            server['ledger_index'],
            server['txn_count'],
            server['time_updated'],
            ])
    print(pretty_table)
    logging.info("Successfully printed updated server table.")

async def update_table_ledger(table, message):
    '''
    Add information from ledger closed messages into the table.

    :param list table: Dictionary for each server being tracked
    :param dict message: Incoming ledger close message

    :rtype: list
    '''

    for server in table:
        if server['url'] == message['server_url']:
            for key in server.keys():
                if key in message['data'].keys():
                    server[key] = message['data'][key]
            server['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
            logging.info(f"Successfully updated the table with ledger closed message from: '{server['url']}'.")

    return table

async def check_state_change(settings, server, message, sms_queue):
    '''
    Check if the server's state changed from the last known state.

    :param list table: Dictionary for each server being tracked (previous state information)
    :param dict message: Message with new information about the server
    :param asyncio.queues.Queue sms_queue: Message queue to send via SMS
    '''
    if server.get('server_status') != message.get('server_status') and server.get('server_status') is not None:
        message_body = str(f"State changed for server: '{server.get('server_name')}'. From: '{server.get('server_status')}'. To: '{message.get('server_status')}'.")
        logging.warning(message_body)
        if settings.SMS is True:
            await sms_queue.put(
                {'phone_from': server['phone_from'], 'phone_to': server['phone_to'], 'message': message_body}
            )

async def update_table_server(settings, table, sms_queue, message):
    '''
    Add info contained in new messages to the table.

    :param settings: Config file
    :param list table: Dictionary for each server being tracked
    :param asyncio.queues.Queue sms_queue: Message queue to send via SMS
    :param dict message: New server subscription message
    '''
    logging.info(f"Server status message received from '{message['server_url']}'. Preparing to update the table.")
    message_result = message['data']['result']

    for server in table:
        if server['url'] is message['server_url']:
            await check_state_change(settings, server, message_result, sms_queue)
            for key in server.keys():
                if key in message_result.keys():
                    server[key] = message_result[key]
            server['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

            logging.info("Successfully updated the server status table.")

    return table

async def create_table_stock(settings):
    '''
    Create a table representing each server in the settings file.
    ### This will have to be updated so the table is not created from settings.####

    :param settings: Config file
    :rtype: list
    '''
    table = []
    for server in settings.SERVERS:
        table.append(
            {
                'server_name': server.get('name'),
                'url': server.get('url'),
                'phone_to': server.get('phone_to'),
                'phone_from': server.get('phone_from'),
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
                'validated_ledgers': None,
                'ledger_index': None,
                'ledger_hash': None,
                'txn_count': None,
                'time_updated': None,
            }
        )
    logging.info("Initial blank server table created.")
    return table
