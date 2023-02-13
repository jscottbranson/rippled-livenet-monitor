'''
Generate the tables used for tracking stock servers and validators.
'''
import logging
from copy import deepcopy

def create_table_stock(settings):
    '''
    Create a table representing each server in the settings file.
    ### This will have to be updated so the table is not created from settings.####

    :param settings: Config file
    :rtype: list
    '''
    table = []
    default_dict = {
        'server_name': None,
        'url': None,
        'ssl_verify': None,
        'command': None,
        'ws_retry_count': 0,
        'ws_connection_task': None,
        'notifications': None,
        'pubkey_node': None,
        'hostid': None,
        'fee_base': None,
        'fee_ref': None,
        'load_base': None,
        'reserve_base': None,
        'reserve_inc': None,
        'load_factor': None,
        #'load_factor_fee_escalation': None,
        #'load_factor_fee_queue': None,
        'load_factor_fee_reference': None,
        'load_factor_server': None,
        'server_status': None,
        'validated_ledgers': None,
        'ledger_index': None,
        'ledger_hash': None,
        'ledger_time':None,
        'forked': None,
        'time_forked': None,
        'txn_count': None,
        'random': None,
        'time_updated': None,
    }

    logging.debug("Preparing to create initial server list.")
    for server in settings.SERVERS:
        server_dict = deepcopy(default_dict)
        for key in server_dict:
            if key in server:
                server_dict[key] = server.get(key)
        table.append(server_dict)
    logging.warning(f"Initial server list created with {len(table)} items.")
    return table

def create_table_validation(settings):
    '''
    Create a dictionary with information on validators identified
    in the settings.
    ### In the future, this should not be created from settings. ###

    :param settings: Configuration file
    :param list val_keys: List of validation keys to monitor

    :rtype: list
    '''
    table = []

    default_dict = {
        'cookie': None,
        'server_version': None,
        'base_fee': None,
        'reserve_base': None,
        'reserve_inc': None,
        'full': None,
        'ledger_hash': None,
        'validated_hash': None,
        'ledger_index': None,
        'signature': None,
        'signing_time': None,
        'load_fee': None,
        'forked': None,
        'time_forked': None,
        'time_updated': None,
        'server_name': None,
        'notifications': None,
        'master_key': None,
        'validation_public_key': None,
    }

    logging.debug("Preparing to build validator dictionaries.")
    for validator in settings.VALIDATORS:
        val_dict = deepcopy(default_dict)
        for key in val_dict:
            if key in validator:
                val_dict[key] = validator.get(key)
        table.append(val_dict)
    logging.warning(f"Successfully created initial validator list with: {len(table)} items.")

    return table
