'''
Functions used across response processor.
'''
import logging
import asyncio
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
