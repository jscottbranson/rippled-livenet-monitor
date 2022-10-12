'''
Process server and ledger subscription messages.
This output is not relevant for monitoring validations.
'''
import logging
import time
import asyncio

from prettytable import PrettyTable
from notifications import notify_twilio

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
    pretty_table = PrettyTable()
    pretty_table.field_names = [
        "Server Name", "State", "Base Load", "Srv Load",
        "Net Load", "Base Fee", "Ref Fee", "Fee Escalation",
        "Queue Fee", "LL Hash", "LL Index", "LL # Tx", "Last Updated"
    ]
    table = await format_table_server(table)
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
            table[key]['ledger_hash'],
            table[key]['ledger_index'],
            table[key]['txn_count'],
            table[key]['time_updated'],
            ])
    print(pretty_table)

async def update_table_ledger(table, message):
    '''
    Add information from ledger closed messages into the table.
    '''
    update = table[message['server_url']]

    update['ledger_index'] = message['data'].get('ledger_index')
    update['ledger_hash'] = message['data'].get('ledger_hash')
    update['txn_count'] = message['data'].get('txn_count')
    update['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

    return table

async def check_state_change(settings, table, message):
    '''
    Check if the server's state changed from the last known state.

    :param dict table: Previous information about the server
    :param dict message: Message with new information about the server
    '''
    if table.get('server_status') != message.get('server_status') and table.get('server_status') is not None:
        #server status changed
        message_body = str(f"State changed for server: {table.get('server_name')}. From: {table.get('server_status')}. To: {message.get('server_status')}.")
        logging.warning(message_body)
        if settings.TWILIO is True:
            response_id = await notify_twilio.send_twilio_sms(settings, message_body)

async def update_table_server(settings, table, message):
    '''
    Add info contained in new messages to the table.

    :param settings: Config file
    :param dict table: Table with server information
    :param dict message: New server subscription message
    '''
    update = table[message['server_url']]
    message = message['data']['result']

    # Check for changes in server state
    await check_state_change(settings, update, message)

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
    return table
