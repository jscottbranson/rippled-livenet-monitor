'''
Check for servers whose last ledger index number is outside of a tolerable range.
'''

import logging
import asyncio

async def calc_modes(values):
    '''
    Return the mode for a list of integers.

    :param list values: Integers
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
        index = table[server].get('ledger_index')
        if index:
            ll_indexes.append(int(index))
    if ll_indexes:
        modes = await calc_modes(ll_indexes)
    logging.info("Successfully calculated mode(s) for LL index across monitored servers.")
    return modes

async def check_diff_mode(settings, table, modes):
    '''
    Check if the servers in the table have different last ledger indexes then the mode.

    :param settings: Config file
    :param dict table: Servers to check for different LL index numbers
    :param list modes: Modes from the broader group of servers we are checking
    '''
    forks = {}
    for server in table:
        index = table[server].get('ledger_index')
        if index:
            if abs(int(modes[0]) - int(index)) > settings.LL_FORK_CUTOFF:
                forks[table[server].get('server_name')] = int(index)
    logging.info("Successfully checked for differences between each monitored server LL index and the mode of all observed LL indexes.")
    return forks

async def alert_forks(settings, forks, sms_queue, modes):
    '''
    Provide appropriate output when a fork is detected.

    :param settings: Config file
    :param dict forks: Forked servers with their names and LL Indexes
    :param asyncio.queues.Queue sms_queue: Outbound notification queue
    :param list modes: Consensus modes
    '''
    for server in forks:
        message = str(f"Forked server: '{server}' Returned index: '{forks[server]}'. The consensus mode was: '{modes[0]}'.")
        logging.warning(message)
        if settings.SMS is True:
            await sms_queue.put(message)
    logging.info("Successfully warned of forked servers: '{forks}'.")

async def fork_checker(settings, table, sms_queue):
    '''
    Execute functions on tables to see if any servers are forked and alert if they are.

    :param settings: Config file
    :param dict table: LL indexes for each server
    :param asyncio.queues.Queue sms_queue: Outbound notification queue
    '''
    logging.info("Checking to see if any servers are forked.")
    modes = await get_modes(table)
    if modes and len(modes) > 1:
        logging.warning(f"Multiple modes found for last ledger indexes: '{modes}' when considering input from: '{len(table)}' servers.")
    else:
        forks = await check_diff_mode(settings, table, modes)
        if forks:
            await alert_forks(settings, forks, sms_queue, modes)

    logging.info("Successfully checked to see if any servers are forked.")
    return forks
