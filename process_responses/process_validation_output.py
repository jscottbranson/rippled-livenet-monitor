'''
Process validation stream messages.
'''
import logging
import time
import asyncio
from copy import deepcopy

from prettytable import PrettyTable

async def format_table_validation(table):
    '''
    Format output for the validation table, so it's human friendly.

    :param list table: Dictionaries for each validator being tracked
    '''
    color_reset = "\033[0;0m"
    green = "\033[0;32m"
    red = "\033[1;31m"
    for validator in table:
        if isinstance(validator['master_key'], str):
            validator['master_key'] = validator['master_key'][:5]
        if isinstance(validator['validation_public_key'], str):
            validator['validation_public_key'] = validator['validation_public_key'][:5]
        if isinstance(validator['ledger_hash'], str):
            validator['ledger_hash'] = validator['ledger_hash'][:5]
        if isinstance(validator['validated_hash'], str):
            validator['validated_hash'] = validator['validated_hash'][:5]
        if validator['forked']:
            validator['forked'] = red + str(validator['forked']) + color_reset
        else:
            validator['forked'] = green + str(validator['forked']) + color_reset
        if validator['full']:
            validator['full'] = green + str(validator['full']) + color_reset
        else:
            validator['full'] = red + str(validator['full']) + color_reset
    return table

async def print_table_validation(table):
    '''
    Print the validation table.

    :param list table: Dictionaries for each validator being tracked
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
            validator['server_name'],
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

    print(pretty_table)
    logging.info("Successfully printed updated validations table.")

async def del_dup_validators(table):
    '''
    Remove duplicate entries from the val_keys list.

    :param list table: Dictionaries for each validator being tracked

    :rtype: (list, list)
    '''
    val_keys = []
    table_new = []

    for validator in table:
        master_key = validator.get('master_key')

        if master_key not in val_keys:
            val_keys.append(master_key)
            table_new.append(validator)
        else:
            logging.warning(f"Removed duplicate validator: '{validator}'.")

    logging.info(f"Finished removing duplicate validators. Original table had: '{len(table)}' items. New table has: '{len(table_new)}' items.")
    return val_keys, table_new

async def clean_validations(settings, val_keys, table, processed_validations):
    '''
    Ensure the processed_validations list doesn't go on forever.

    If set, ensure the same validator isn't monitored twice.

    :param settings: Config file
    :param list val_keys: Master or ephemeral validation keys we are monitoring for
    :param list table: Dictionaries for each validator being tracked
    :param list processed_validations: Prune this
    '''
    if len(processed_validations) >= settings.PROCESSED_VAL_MAX:
        half_list = settings.PROCESSED_VAL_MAX / 2
        logging.info(f"Processed validation list >= '{settings.PROCESSED_VAL_MAX}'. Deleting: '{half_list}' items.")
        del processed_validations[0:int(half_list)]

        if settings.REMOVE_DUP_VALIDATORS:
            val_keys, table = await del_dup_validators(table)
    return val_keys, table, processed_validations

async def update_table_validator(table, message):
    '''
    Update the table based on a received validation message.

    :param list table: Dictionaries for each validator being tracked
    :param dict message: JSON decoded message to add to the table
    '''
    message = message['data']

    for validator in table:
        if message.get('master_key') == validator['master_key'] or message.get('validation_public_key') == validator['validation_public_key']:
            for key in validator.keys():
                if key in message.keys():
                    validator[key] = message[key]
    logging.info("Successfully updated validator table.")

    return table

async def process_validations(settings, val_keys, table_validator, processed_validations, message):
    '''
    Process unique validation messages.
    :param settings: Configuration file
    :param list val_keys: master and ephemeral validation keys to monitor for
    :param list table_validator: Dictionaries for each validator being tracked
    :param list processed_validations: Validation messages we already processed (avoid
    processing duplicate messages)
    :param dict message: JSON decoded message to process
    '''
    # Update the table
    logging.info(f"Preparing to update validator table based on message from '{message['server_url']}'.")
    table_validator = await update_table_validator(table_validator, message)
    logging.info(f"Updated validator table based on message from '{message['server_url']}'.")
    # Add the message so we don't process duplicates
    processed_validations.append(message['data']['signature'])
    logging.info(f"Appended validation from '{message['server_url']}' to received tracking queue.")
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
    :param list table_validator: Dictionaries for each validator being tracked
    :param list processed_validations: Validation messages we already processed (avoid
    processing duplicate messages)
    :param dict message: JSON decoded message to process
    '''
    logging.debug(f"New validation message from '{message['server_url']}'.")
    if message['data'].get('master_key') in val_keys or message['data'].get('validation_public_key') in val_keys:
        if message['data']['signature'] not in processed_validations:
            val_keys, table_validator, processed_validations = await process_validations(
                settings, val_keys, table_validator, processed_validations, message
            )
    else:
        logging.debug(f"Ignored validation message from: '{message['server_url']}'.")

    return val_keys, table_validator, processed_validations


async def create_table_validation(settings):
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
        'time_updated': None,
        'server_name': None,
        'phone_from': None,
        'phone_to': None,
        'master_key': None,
        'validation_public_key': None,
    }

    logging.info("Preparing to build validator dictionaries.")
    for validator in settings.VALIDATOR_MASTER_KEYS + settings.VALIDATOR_EPH_KEYS:
        val_dict = default_dict.copy()
        for key in val_dict:
            val_dict[key] = validator.get(key)
        table.append(val_dict)
    logging.warning(f"Successfully created initial validator list with: {len(table)} items.")

    return table
