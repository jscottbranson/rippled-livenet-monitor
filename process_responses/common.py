'''
Functions used across response processor.
'''
import logging
from copy import deepcopy


async def copy_stock(table_stock):
    '''
    Copy a list of dictionaries describing the stock servers being tracked while
    excluding websocket connection objects.

    :param list table_stock: Stock servers being monitored
    '''
    table_stock_new = []

    for server in table_stock:
        table_stock_new.append(
            {x: deepcopy(server[x]) for x in server if x != 'ws_connection_task'}
        )
    return table_stock_new

async def decode_version(version):
    '''
    Decode XRP Ledger version numbers.
    This is basically a Python3 translation of the XRPScan XRPL-Server-Version
    repo: https://github.com/xrpscan/xrpl-server-version/blob/main/index.js

    :param int version: Version integer from a XRP Ledger server

    :param returns: Human readable version information
    :param rtype: dict
    '''
    implementations = {
        '183b': 'rippled',
    }

    release_types = {
        '10': 'RC',
        '01': 'beta',
    }

    decoded_version = {}

    # Convert from integer to a string binary with 0 padding on the left
    version_bin = format(int(version), '064b')

    # Decode Implementation ID
    imp_bin = version_bin[0:16]
    imp_hex = format(int(imp_bin, 2), 'x')

    if imp_hex in implementations:
        decoded_version['implementation'] = implementations[imp_hex]
    else:
        decoded_version['implementation'] = 'unknown'

    # Decode Major Version
    decoded_version['major'] = int(version_bin[16:24], 2)

    # Decode Minor Version
    decoded_version['minor'] = int(version_bin[24:32], 2)

    # Decoded Patch Version
    decoded_version['patch'] = int(version_bin[32:40], 2)

    # Decode Release Type and number (if not a major release)
    release_type_bin = version_bin[40:42]
    if release_type_bin in release_types:
        decoded_version['release_type'] = release_types[release_type_bin]
        decoded_version['release_number'] = int(version_bin[42:48], 2)
    else:
        decoded_version['release_type'] = ''
        decoded_version['release_number'] = ''

    # Put it all together
    version_number = \
            f"{decoded_version.get('implementation')} " \
            + f"{decoded_version.get('major')}." \
            + f"{decoded_version.get('minor')}." \
            + f"{decoded_version.get('patch')}"
    decoded_version['version_number'] = version_number.strip()

    version_final = \
            f"{decoded_version.get('version_number')} " \
            + f"{decoded_version.get('release_type')} " \
            + f"{decoded_version.get('release_number')}"
    decoded_version['version'] = version_final.strip()

    return decoded_version
