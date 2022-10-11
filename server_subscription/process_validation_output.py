'''
Process validation stream messages.
'''
import logging
import time
import asyncio

from prettytable import PrettyTable

async def format_table_validation(table):
    '''
    Format output for the validation table, so it's human friendly.
    '''
    for key in table:
        if isinstance(table[key]['master_key'], str):
            table[key]['master_key'] = table[key]['master_key'][:5]
        if isinstance(table[key]['validation_public_key'], str):
            table[key]['validation_public_key'] = table[key]['validation_public_key'][:5]
        if isinstance(table[key]['ledger_hash'], str):
            table[key]['ledger_hash'] = table[key]['ledger_hash'][:5]
    return table

async def print_table_validation(table):
    '''
    Print the validation table.
    '''
    pretty_table = PrettyTable()
    pretty_table.field_names = [
        "Server", "Master Key", "Eph Key", "Full?", "LL Hash", "LL Index", "Last Updated",
    ]

    table = await format_table_validation(table)

    for key in table:
        pretty_table.add_row([
            table[key]['server_name'],
            table[key]['master_key'],
            table[key]['validation_public_key'],
            table[key]['full'],
            table[key]['ledger_hash'],
            table[key]['ledger_index'],
            table[key]['time_updated'],
        ])

    print(pretty_table)

async def clean_validations(settings, val_keys, table_validator, processed_validations):
    '''
    Ensure the processed_validations list doesn't go on forever.

    Ensure the same validator isn't being monitored twice (due to a duplicate entry in
    the settings file.
    :param settings: Config file
    :param list val_keys: Master or ephemeral validation keys we are monitoring for
    :param list processed_validations: Prune this
    '''
    if len(processed_validations) >= settings.PROCESSED_VAL_MAX:
        half_list = settings.PROCESSED_VAL_MAX / 2
        logging.info(f"Processed validation list >= {settings.PROCESSED_VAL_MAX}. Deleting {half_list} items.")
        del processed_validations[0:int(half_list)]

        val_keys, table_validator = await update_val_keys(val_keys, table_validator)
    return val_keys, table_validator, processed_validations

async def update_table_validator(table, message):
    '''
    Update the table based on a received validation message.
    :param dict table_validator: Table for aggregating validation messages
    :param dict message: JSON decoded message to add to the table
    '''
    message = message['data']
    update = None
    if message['master_key'] in table.keys():
        update = table[message['master_key']]
    elif message['validation_public_key'] in table.keys():
        update = table[message['validation_public_key']]

    update['full'] = message.get('full')
    update['ledger_hash'] = message.get('ledger_hash')
    update['ledger_index'] = message.get('ledger_index')
    update['master_key'] = message.get('master_key')
    update['validation_public_key'] = message.get('validation_public_key')
    update['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

    return table

async def update_val_keys(val_keys, table):
    '''
    Remove duplicate entries from the val_keys list.
    :param list val_keys: Keys from validators we want to monitor
    :param dict table: Includes master/ephemeral key mappings
    '''
    to_remove = []
    for validator in table:
        master = table[validator].get('master_key')
        eph = table[validator].get('validation_public_key')

        if isinstance(master, str) and isinstance(eph, str):
            if master in val_keys and eph in val_keys:
                logging.warning(f"Duplicate validator found in settings. Master key: {master}. Ephemeral key: {eph}. Deleting duplicate ephemeral key from tracking list.")
                to_remove.append(eph)

    for key in to_remove:
        val_keys.remove(key)
        table.pop(key)

    return val_keys, table

async def process_validations(settings, val_keys, table_validator, processed_validations, message):
    '''
    Process unique validation messages.
    :param settings: Configuration file
    :param list val_keys: master and ephemeral validation keys to monitor for
    :param dict table_validator: Table for aggregating validation messages
    :param list processed_validations: Validation messages we already processed (avoid
    processing duplicate messages)
    :param dict message: JSON decoded message to process
    '''
    # Update the table
    logging.info(f"Preparing to update validator table based on message from {message['server_url']}.")
    table_validator = await update_table_validator(table_validator, message)
    logging.info(f"Updated validator table based on message from {message['server_url']}.")
    # Add the message so we don't process duplicates
    processed_validations.append(message['data']['signature'])
    logging.info(f"Appended validation from {message['server_url']} to received tracking queue.")
    # Prune received message queue
    logging.info("Checking to see if we need to clean things")
    val_keys, table_validator, processed_validations = await clean_validations(
        settings, val_keys, table_validator, processed_validations
    )

    logging.info("Done processing validation message.")
    return val_keys, table_validator, processed_validations

async def check_validations(settings, val_keys, table_validator, processed_validations, message):
    '''
    Check to see if we should continue processing validation messages.

    :param settings: Configuration file
    :param list val_keys: master and ephemeral validation keys to monitor for
    :param dict table_validator: Table for aggregating validation messages
    :param list processed_validations: Validation messages we already processed (avoid
    processing duplicate messages)
    :param dict message: JSON decoded message to process
    '''
    # Only attend to messages from servers we are monitoring
    if message['data'].get('master_key') in val_keys or message['data'].get('validation_public_key') in val_keys:
        # Ignore duplicate validation messages
        if message['data']['signature'] not in processed_validations:
            val_keys, table_validator, processed_validations = await process_validations(
                settings, val_keys, table_validator, processed_validations, message
            )
    else:
        logging.info(f"Ignored validation message from: {message['server_url']}.")

    return val_keys, table_validator, processed_validations

async def create_table_validation(settings):
    '''
    Create a dictionary with information on validators identified
    in the settings.
    :param settings: Configuration file
    :param list val_keys: List of validation keys to monitor
    '''
    table = {}
    for validator in settings.VALIDATOR_MASTER_KEYS:
        table[validator['key']] = {
            'server_name': validator['name'],
            'full': None,
            'ledger_hash': None,
            'ledger_index': None,
            'master_key': validator['key'],
            'validation_public_key': None,
            'time_updated': None,
        }

    for validator in settings.VALIDATOR_EPH_KEYS:
        table[validator['key']] = {
            'server_name': validator['name'],
            'full': None,
            'ledger_hash': None,
            'ledger_index': None,
            'master_key': None,
            'validation_public_key': validator['key'],
            'time_updated': None,
        }

    return table
