'''
Make pretty console output.
'''
import logging
import textwrap
from copy import deepcopy

from prettytable import PrettyTable, ALL

from .common import decode_version
from .common import copy_stock


# Validator table output
async def format_table_validation(table):
    '''
    Format output for the validation table, so it's human friendly.

    :param list table: Dictionaries for each validator being tracked.
    '''
    color_reset = "\033[0;0m"
    green = "\033[0;32m"
    red = "\033[1;31m"
    for validator in table:
        # Shorten keys and hashes
        if isinstance(validator['master_key'], str):
            validator['master_key'] = validator['master_key'][:5]
        if isinstance(validator['validation_public_key'], str):
            validator['validation_public_key'] = validator['validation_public_key'][:5]
        if isinstance(validator['ledger_hash'], str):
            validator['ledger_hash'] = validator['ledger_hash'][:5]
        if isinstance(validator['validated_hash'], str):
            validator['validated_hash'] = validator['validated_hash'][:5]
        # Green if not forked
        if validator['forked'] is False:
            validator['forked'] = green + str(validator['forked']) + color_reset
        else:
            validator['forked'] = red + str(validator['forked']) + color_reset
            validator['server_name'] = red + validator['server_name'] + color_reset
        # Green if validations are full
        if validator['full']:
            validator['full'] = green + str(validator['full']) + color_reset
        else:
            validator['full'] = red + str(validator['full']) + color_reset
            validator['server_name'] = red + validator['server_name'] + color_reset
        # Calculate server version
        if isinstance(validator['server_version'], str):
            if validator['server_version'][0:].isdigit():
                server_version = await decode_version(validator['server_version'])
                validator['server_version'] = server_version.get('version')
    return table

async def print_table_validation(table):
    '''
    Print the validation table.

    :param list table: Dictionaries for each validator being tracked.
    '''
    logging.info("Preparing to print updated validations table.")
    pretty_table = PrettyTable()
    pretty_table.field_names = [
        "Validator Name", "Master Key", "Eph Key", "Version", "Base Fee", "Local LL Fee",
        "LL Hash", "LL Index", "Full?", "Forked?", "Last Updated",
    ]

    table_new = await format_table_validation(deepcopy(table))

    for validator in table_new:
        pretty_table.add_row([
            validator['server_name'].lower(),
            validator['master_key'],
            validator['validation_public_key'],
            validator['server_version'],
            validator['base_fee'],
            validator['load_fee'],
            validator['ledger_hash'],
            validator['ledger_index'],
            validator['full'],
            validator['forked'],
            validator['time_updated'],
        ])

    pretty_table.sortby = "Validator Name"
    print(pretty_table)
    logging.info("Successfully printed updated validations table.")

#Server table console output.
async def fee_calc(fee, base_fee, multiple):
    '''
    Calculate a fee and apply color if it's elevated.
    '''
    color_reset = "\033[0;0m"
    green = "\033[0;32m"
    red = "\033[1;31m"
    if isinstance(fee, int) and isinstance(base_fee, int) and isinstance(multiple, int):
        calc_fee = round(fee / multiple * base_fee, 1)
        if calc_fee > base_fee:
            calc_fee = red + str(calc_fee) + color_reset
        elif calc_fee == base_fee:
            calc_fee = green + str(calc_fee) + color_reset
        else:
            calc_fee = fee
    elif isinstance(base_fee, int):
        calc_fee = green + str(base_fee) + color_reset
    else:
        calc_fee = fee
    return calc_fee

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
        # Shorten ledger hashes
        if isinstance(server['ledger_hash'], str):
            server['ledger_hash'] = server['ledger_hash'][:5]
        # Full servers in green
        if isinstance(server['server_status'], str):
            if server['server_status'] == "full":
                server['server_status'] = green + server['server_status'] + color_reset
            else:
                server['server_status'] = red + server['server_status'] + color_reset
                server['server_name'] = red + str(server['server_name']) + color_reset
        # Forked Servers in Red
        if server['forked'] is False:
            server['forked'] = green + str(server['forked']) + color_reset
        else:
            server['forked'] = red + str(server['forked']) + color_reset
            server['server_name'] = red + str(server['server_name']) + color_reset
        # Base load factor in green
        if isinstance(server['load_factor'], int) and isinstance(server['load_base'], int):
            if server['load_factor'] == server['load_base']:
                server['load_factor'] = round(server['load_factor'] / server['load_base'], 1)
                server['load_factor'] = green + str(server['load_factor']) + color_reset
            else:
                server['load_factor'] = round(server['load_factor'] / server['load_base'], 1)
                server['load_factor'] = red + str(server['load_factor']) + color_reset
        # Calculate Open Ledger Fee
        server['load_factor_fee_escalation'] = await fee_calc(
            server['load_factor_fee_escalation'], server['fee_base'], server['load_base']
        )
        # Calculate Queue Fee
        server['load_factor_fee_queue'] = await fee_calc(
            server['load_factor_fee_queue'], server['fee_base'], server['load_base']
        )
    return table

async def print_table_server(table):
    '''
    Print a pretty table to the console.

    :param list table: Dictionary for each server being tracked
    '''
    logging.info("Preparing to print updated server table.")
    pretty_table = PrettyTable()
    pretty_table.field_names = [
        "Server Name", "State", "O.L. Fee", "Queue Fee", "Load Multiplier",
        "LL Hash", "History", "LL # Tx", "Forked?", "Last Updated",
    ]
    table_new = await format_table_server(await copy_stock(table))

    for server in table_new:
        pretty_table.add_row([
            server['server_name'],
            server['server_status'],
            server['load_factor_fee_escalation'],
            server['load_factor_fee_queue'],
            server['load_factor'],
            server['ledger_hash'],
            server['validated_ledgers'],
            server['txn_count'],
            server['forked'],
            server['time_updated'],
            ])
    pretty_table.sortby = "Server Name"
    print(pretty_table)
    logging.info("Successfully printed updated server table.")

async def sort_amendments(table_validator, amendments):
    '''
    Aggregate amendment votes.

    :param dict table_validator: Validator tracking table.
    :param dict amendments: Known amendment IDs mapped to their names.
    '''
    for amendment in amendments:
        amendment['supporters'] = []
        for validator in table_validator:
            if isinstance(validator['amendments'], list):
                if amendment['id'] in validator['amendments']:
                    amendment['supporters'].append(validator['server_name'])

    return amendments

async def format_amendment(amendment, table_validator):
    '''
    Color and other fun things!
    '''
    color_reset = "\033[0;0m"
    green = "\033[0;32m"

    amendment['supporters'].sort(key=str.lower)

    support_percent = round(len(amendment['supporters']) / len(table_validator) * 100, 1)
    if support_percent > 80:
        amendment['name'] = green + str(amendment['name']) + color_reset
        amendment['support_percent'] = green + str(support_percent) + color_reset
    else:
        amendment['support_percent'] = str(support_percent)
    return amendment

async def print_table_amendments(table_validator, amendments):
    '''
    Print information on amendment voting.

    :param dict table_validator: Validator tracking table.
    :param dict amendments: Known amendment IDs mapped to their names.
    '''
    logging.info("Preparing to print updated amendments table.")
    pretty_table=PrettyTable()
    pretty_table.field_names = [
        "Amendment",
        "Yea Votes",
        "Nay Votes",
        "% Support",
        "Supporters",
    ]

    amendment_votes = await sort_amendments(table_validator, deepcopy(amendments))
    for amendment in amendment_votes:
        amendment = await format_amendment(amendment, table_validator)
        supporters = ''
        for supporter in amendment['supporters']:
            supporters = supporters + supporter + ', '
        pretty_table.add_row([
            amendment['name'],
            len(amendment['supporters']),
            len(table_validator) - len(amendment['supporters']),
            amendment['support_percent'],
            textwrap.fill(supporters, width=180),
        ])
    pretty_table.hrules=ALL
    pretty_table.sortby = "Yea Votes"
    pretty_table.reversesort = True
    print(pretty_table)
    logging.info("Successfully printed the amendments table.")
