'''
Check for servers whose last ledger index number is outside of a tolerable range.
'''
import time
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

    :param settings: Config file
    :param list table: Dictionary for each server or validator being monitored
    :param list modes: Modes from the broader group of servers we are checking
    '''
    forks_new = []
    for server in table:
        index = server.get('ledger_index')
        if index and server.get('server_status') != "disconnected from monitoring":
            if abs(int(modes[0]) - int(index)) > settings.LL_FORK_CUTOFF:
                forks_new.append(
                    {
                        'server_name': server.get('server_name'),
                        'phone_from': server.get('phone_from'),
                        'phone_to': server.get('phone_to'),
                        'ledger_index': index,
                        'time_forked': time.time(),
                    }
                )
    logging.info("Successfully checked for differences between each monitored server LL index and the mode of all observed LL indexes.")
    return forks_new

async def alert_resolved_forks(settings, forks, sms_queue):
    '''
    Provide output when a forked server rejoins the network.

    :param settings: Config file
    :param dict forks: Forked servers with their names and LL Indexes
    :param asyncio.queues.Queue sms_queue: Outbound notification queue
    '''
    for server in forks:
        message = str(f"Previously forked server: '{server.get('server_name')}' appears to be back in consensus.")
        logging.warning(message)
        if settings.SMS is True:
            sms = {'message': message, 'phone_from': server.get('phone_from'), 'phone_to': server.get('phone_to')}
            await sms_queue.put(sms)
    logging.info("Successfully warned of previously forked servers: '{forks}'.")

async def alert_new_forks(settings, forks, sms_queue, modes):
    '''
    Provide appropriate output when a fork is detected.

    :param settings: Config file
    :param dict forks: Forked servers with their names and LL Indexes
    :param asyncio.queues.Queue sms_queue: Outbound notification queue
    :param list modes: Consensus modes
    '''
    for server in forks:
        message = str(f"Forked server: '{server.get('server_name')}' Returned index: '{server.get('ledger_index')}'. The consensus mode was: '{modes[0]}'.")
        logging.warning(message)
        if settings.SMS is True:
            sms = {'message': message, 'phone_from': server.get('phone_from'), 'phone_to': server.get('phone_to')}
            await sms_queue.put(sms)
    logging.info("Successfully warned of forked servers: '{forks}'.")

async def check_fork_changes(old_forks, new_forks):
    '''
    Evaluate previously forked servers to see if they are no longer forked.
    Depending on settings, alerts should be sent when servers return to the main network.

    :param settings: Config file
    :param list forks_old: Previously forked servers
    :param list forks_new: Currently forked servers
    '''
    names_new = []
    names_old = []
    forks_new_names = []
    forks_resolved_names = []
    forks_new = []
    forks_resolved = []

    for server in old_forks:
        names_old.append(server.get('server_name'))
    for server in new_forks:
        names_new.append(server.get('server_name'))

    for server in names_old:
        if server not in names_new:
            forks_resolved_names.append(server)
    for server in names_new:
        if server not in names_old:
            forks_new_names.append(server)

    for server in old_forks:
        if server['server_name'] in forks_resolved_names:
            forks_resolved.append(server)
    for server in new_forks:
        if server['server_name'] in forks_new_names:
            forks_new.append(server)

    return forks_new, forks_resolved

async def fork_checker(settings, table, sms_queue, forks_old):
    '''
    Execute functions on tables to see if any servers are forked and alert if they are.

    :param settings: Config file
    :param list table: Dictionary for each server and validator being tracked
    :param asyncio.queues.Queue sms_queue: Outbound notification queue
    :param list forks_old: Dictionaries describing each of the previously forked servers or validators

    :rtype: list
    '''
    forks_new = []
    logging.info("Checking to see if any servers are forked.")
    modes = await get_modes(table)
    if modes and len(modes) > 1:
        logging.warning(f"Multiple modes found for last ledger indexes: '{modes}' when considering input from: '{len(table)}' servers. Skipping fork check.")
        forks_new = forks_old
    else:
        forks_new = await check_diff_mode(settings, table, modes)
        forks_new_alert, forks_resolved_alert = await check_fork_changes(forks_old, forks_new)
        if forks_new_alert:
            await alert_new_forks(settings, forks_new_alert, sms_queue, modes)
        if forks_resolved_alert:
            await alert_resolved_forks(settings, forks_resolved_alert, sms_queue)
    logging.info("Successfully checked to see if any servers are forked.")
    return forks_new
