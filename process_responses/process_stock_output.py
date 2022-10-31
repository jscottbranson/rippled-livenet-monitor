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

async def print_table_server(table):
    '''
    Print a pretty table to the console.
    '''
    logging.info("Preparing to print updated server table.")
    pretty_table = PrettyTable()
    pretty_table.field_names = [
        "Server Name", "State", "Base Load", "Srv Load",
        "Net Load", "Base Fee", "Ref Fee", "Fee Escalation",
        "Queue Fee", "LL Hash", "LL Index", "LL # Tx", "Last Updated"
    ]
    table_new = await format_table_server(deepcopy(table))
    for key in table_new:
        pretty_table.add_row([
            table_new[key]['server_name'],
            table_new[key]['server_status'],
            table_new[key]['load_base'],
            table_new[key]['load_factor_server'],
            table_new[key]['load_factor'],
            table_new[key]['fee_base'],
            table_new[key]['fee_ref'],
            table_new[key]['load_factor_fee_escalation'],
            table_new[key]['load_factor_fee_queue'],
            table_new[key]['ledger_hash'],
            table_new[key]['ledger_index'],
            table_new[key]['txn_count'],
            table_new[key]['time_updated'],
            ])
    print(pretty_table)
    logging.info("Successfully printed updated server table.")

async def update_table_ledger(table, message):
    '''
    Add information from ledger closed messages into the table.
    '''
    logging.info(f"New ledger closed message from '{message['server_url']}'.")
    update = table[message['server_url']]

    update['ledger_index'] = message['data'].get('ledger_index')
    update['ledger_hash'] = message['data'].get('ledger_hash')
    update['txn_count'] = message['data'].get('txn_count')
    update['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
    logging.info(f"Successfully updated the table with ledger closed message from: '{message['server_url']}'.")

    return table

async def check_state_change(settings, table, message, sms_queue):
    '''
    Check if the server's state changed from the last known state.

    :param dict table: Previous information about the server
    :param dict message: Message with new information about the server
    :param asyncio.queues.Queue sms_queue: Message queue to send via SMS
    '''
    if table.get('server_status') != message.get('server_status') and table.get('server_status') is not None:
        message_body = str(f"State changed for server: '{table.get('server_name')}'. From: '{table.get('server_status')}'. To: '{message.get('server_status')}'.")
        logging.warning(message_body)
        if settings.SMS is True:
            await sms_queue.put(
                {'phone_from': settings.NUMBER_FROM, 'phone_to': settings.NUMBER_TO, 'message': message_body}
            )

async def update_table_server(settings, table, sms_queue, message):
    '''
    Add info contained in new messages to the table.

    :param settings: Config file
    :param dict table: Table with server information
    :param asyncio.queues.Queue sms_queue: Message queue to send via SMS
    :param dict message: New server subscription message
    '''
    logging.info(f"Server status message received from '{message['server_url']}'. Preparing to update the table.")
    update = table[message['server_url']]
    message = message['data']['result']

    await check_state_change(settings, update, message, sms_queue)

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

    logging.info("Successfully updated the server status table.")

    return table

async def create_table_stock(settings):
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
    logging.info("Initial blank server table created.")
    return table