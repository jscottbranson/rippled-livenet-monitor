'''
Check for servers whose last ledger index number is outside of a tolerable range.
'''
import time
import logging
from copy import deepcopy
import asyncio

from .common import copy_stock

async def calc_modes(values):
    '''
    Return the mode for a list of integers.

    :param list values: Integers

    :return: Last ledger index modes
    :rtype: list
    '''
    counts = {}
    for i in values:
        if i in counts:
            counts[i] += 1
        else:
            counts[i] = 1
    return [key for key in counts.keys() if counts[key] == max(counts.values())]

async def get_modes(table):
    '''
    Extract LL index numbers from a dictionary and check their mode(s).

    :param dict table: Servers with ledger_index values
    '''
    ll_indexes = []
    modes = None
    for server in table:
        index = server.get('ledger_index')
        if index:
            ll_indexes.append(int(index))
    if ll_indexes:
        modes = await calc_modes(ll_indexes)
    logging.info("Successfully calculated mode(s) for LL index across monitored servers.")
    return modes

async def check_diff_mode(settings, table, modes):
    '''
    Check if the servers in the table have different last ledger indexes then the mode.

    :param list table: Stock server tracking table and validator tracking table
    :param list modes: Modes from the broader group of servers we are checking
    '''
    for server in table:
        index = server.get('ledger_index')
        if index and server.get('server_status') != "disconnected from monitoring":
            if abs(int(modes[0]) - int(index)) > settings.LL_FORK_CUTOFF:
                if not server.get('forked'):
                    server['time_forked'] = time.time()
                server['forked'] = True
            else:
                server['time_forked'] = None
                server['forked'] = False
    logging.info("Checked for differences between monitored server LL index and the mode of all observed LL indexes.")
    return table

async def alert_resolved_forks(forks, notification_queue):
    '''
    Provide output when a forked server rejoins the network.

    :param settings: Config file
    :param dict forks: Forked servers with their names and LL Indexes
    :param asyncio.queues.Queue notification_queue: Outbound notification queue
    '''
    for server in forks:
        now = time.strftime("%m-%d %H:%M:%S", time.gmtime())
        message = str(f"Previously forked server: '{server.get('server_name')}' is in consensus. Time UTC: {now}.")
        logging.warning(message)
        notification_queue.put({'message': message, 'server': server,})
    logging.info("Successfully warned of previously forked servers: '{forks}'.")

async def alert_new_forks(forks, notification_queue, modes):
    '''
    Provide appropriate output when a fork is detected.

    :param dict forks: Forked servers with their names and LL Indexes
    :param asyncio.queues.Queue notification_queue: Outbound notification queue
    :param list modes: Consensus modes
    '''
    for server in forks:
        now = time.strftime("%m-%d %H:%M:%S", time.gmtime())
        message = str(f"Forked server: '{server.get('server_name')}' Returned index: '{server.get('ledger_index')}'. The consensus mode was: '{modes[0]}'. Time UTC: {now}.")
        logging.warning(message)
        notification_queue.put({'message': message, 'server': server,})
    logging.info("Successfully warned of forked servers: '{forks}'.")

async def create_unique_id(server):
    '''
    Create a unique identifier for each server, since Xahau UNL contains duplicates with the same domain names.
    '''
    server_id = str()
    identifiers = ['server_name', 'master_key', 'validation_public_key', 'cookie']
    for i in identifiers:
        if server.get(i, "novalue") is not None:
            server_id += server.get(str(i), "_no_value")
        else:
            server_id += "__no_value"
    logging.info(f"Server ID generated: {server_id}")
        
    return str(server_id)

async def check_fork_changes(old_tables, new_tables):
    '''
    Evaluate previously forked servers to see if they are no longer forked.
    Depending on settings, alerts should be sent when servers return to the main network.

    :param settings: Config file
    :param list old_tables: Stock and validator tables from before new forks were identified
    :param list new_tables: Stock and validator tables after new forks were identified
    '''
    forks_new = []
    forks_resolved = []

    old_tables = old_tables[0] + old_tables[1]
    new_tables = new_tables[0] + new_tables[1]

    logging.info("Checking for changes in forks.")
    for new_server in new_tables:
        new_server_id = await create_unique_id(new_server)
        for old_server in old_tables:
            old_server_id = await create_unique_id(old_server)
            try:
                if old_server_id == new_server_id\
                   and old_server.get('forked') is not None \
                   and old_server.get('forked') is not new_server.get('forked'):
                    if old_server.get('forked') is False and new_server.get('forked') is True:
                        forks_new.append(new_server)
                    elif old_server.get('forked') is True and new_server.get('forked') is False:
                        forks_resolved.append(new_server)
                    else:
                        logging.warning(f"Confused by new server:\n'{new_server}'\nOld server: '{old_server}'.")
            except Exception as error:
                logging.warning(f"Error checking for changes in new/resolved forks: {error}")
    logging.info("Done checking for changes in forks.")
    return forks_new, forks_resolved

async def fork_checker(settings, table_stock, table_validator, notification_queue):
    '''
    Execute functions on tables to see if any servers are forked and alert if they are.

    :param settings: Config file
    :param list table_stock: Dictionary for each server being tracked
    :param list table_validator: Dictionary for each validator being tracked
    :param asyncio.queues.Queue notification_queue: Outbound notification queue

    :return: Last ledger index modes
    :return: Updated stock server table
    :return: Updated validator server table
    :rtype: list
    '''
    logging.info("Checking to see if any servers are forked.")
    previous_tables = [await copy_stock(table_stock), deepcopy(table_validator)]
    modes = await get_modes(table_stock + table_validator)
    if modes and len(modes) > 1:
        logging.info(f"Multiple modes found for last ledger indexes: '{modes}'. Skipping fork check.")
    else:
        table_stock = await check_diff_mode(settings, table_stock, modes)
        table_validator = await check_diff_mode(settings, table_validator, modes)
        forks_new, forks_resolved = await check_fork_changes(previous_tables, [table_stock, table_validator])
        if forks_new:
            await alert_new_forks(forks_new, notification_queue, modes)
        if forks_resolved:
            await alert_resolved_forks(forks_resolved, notification_queue)
    logging.info("Successfully checked to see if any servers are forked.")
    return modes, table_stock, table_validator
