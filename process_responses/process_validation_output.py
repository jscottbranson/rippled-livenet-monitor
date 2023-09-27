'''
Process validation stream messages.
'''
import logging
import time
import asyncio
from copy import deepcopy


async def del_dup_validators(table):
    '''
    Remove duplicate entries from the val_keys list.

    :param list table: Dictionaries for each validator being tracked

    :rtype: (list, list)
    '''
    val_keys = []
    table_new = []

    for validator in table:
        if validator.get('master_key') not in val_keys:
            val_keys.append(validator.get('master_key'))
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

    # Consider notifying if the ephemeral key changes for a server

    for validator in table:
        if message.get('master_key') and message.get('master_key') == validator['master_key'] \
           or message.get('validation_public_key') == validator['validation_public_key']:
            for key in validator.keys():
                if key in message.keys():
                    validator[key] = message[key]
            validator['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
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
    # Prune received message queue and remove duplicate validators from tracking (depending on settings)
    logging.info("Checking to see if we need to clean things")
    val_keys, table_validator, processed_validations = await clean_validations(
        settings, val_keys, table_validator, processed_validations
    )

    logging.info("Done processing validation message.")
    return val_keys, table_validator, processed_validations

async def log_validations(settings, message):
    '''
    Log validations defined in the settings file.
    '''
    if message['data'].get('master_key') in settings.LOG_VALIDATIONS_FROM:
        logging.critical(f"Logged validation: '{message}'.")

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
    logging.debug(f"New validation message from '{message.get('server_url')}'.")
    if message['data'].get('master_key') in val_keys or message['data'].get('validation_public_key') in val_keys \
       and message['data'].get('validation_public_key'):
        if message['data']['signature'] not in processed_validations:
            val_keys, table_validator, processed_validations = await process_validations(
                settings, val_keys, table_validator, processed_validations, message
            )
            await log_validations(settings, message)
    else:
        logging.debug(f"Ignored validation message from: '{message['server_url']}'.")

    return val_keys, table_validator, processed_validations
