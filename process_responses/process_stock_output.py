'''
Process server and ledger subscription messages.
This output is not relevant for monitoring validations.
'''
import logging
import time
import asyncio

from prettytable import PrettyTable

from .common import copy_stock

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
        if server['forked'] is False:
            server['forked'] = green + str(server['forked']) + color_reset
        else:
            server['forked'] = red + str(server['forked']) + color_reset
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
        "Net Load", "Base Fee", "Ref Fee",
        "LL Hash", "History", "LL # Tx", "Forked?", "Last Updated",
    ]
    table_new = await format_table_server(await copy_stock(table))

    for server in table_new:
        pretty_table.add_row([
            server['server_name'],
            server['server_status'],
            server['load_base'],
            server['load_factor_server'],
            server['load_factor'],
            server['fee_base'],
            server['fee_ref'],
            server['ledger_hash'],
            server['validated_ledgers'],
            server['txn_count'],
            server['forked'],
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
            server['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.gmtime())
            logging.info(f"Successfully updated the table with ledger closed message from: '{server['url']}'.")

    return table

async def check_state_change(server, message, notification_queue):
    '''
    Check if the server's state changed from the last known state.

    :param list table: Dictionary for each server being tracked (previous state information)
    :param dict message: Message with new information about the server
    :param asyncio.queues.Queue notification_queue: Outbound message queue
    '''
    if server.get('server_status') != message.get('server_status') \
       and server.get('server_status') is not None:
        now = time.strftime("%m-%d %H:%M:%S", time.gmtime())

        body = "State changed for server: "
        body = body + str(f"'{server.get('server_name')}'. ")
        body = body + str(f"From: '{server.get('server_status')}'. ")
        body = body + str(f"To: '{message.get('server_status')}'. ")
        body = body + str(f"Time UTC: {now}.")

        logging.warning(body)
        notification_queue.put(
            {
                'message': body,
                'server': server,
            }
        )

async def update_table_server(table, notification_queue, message):
    '''
    Add info contained in new messages to the table.

    :param settings: Config file
    :param list table: Dictionary for each server being tracked
    :param asyncio.queues.Queue notification_queue: Message queue to send via SMS
    :param dict message: New server subscription message
    '''
    logging.info(f"Server status message received '{message}'. Preparing to update the table.")
    if message['data'].get('result'):
        message_result = message['data']['result']
    elif message['data'].get('type') == 'serverStatus':
        message_result = message['data']

    for server in table:
        if server['url'] == message['server_url']:
            await check_state_change(server, message_result, notification_queue)
            for key in message_result.keys():
                if key in server.keys():
                    server[key] = message_result[key]
            server['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

            logging.info("Successfully updated the server status table.")

    return table
