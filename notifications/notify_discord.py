'''
Send messages via Discord webhook.
'''
import logging
import asyncio

import aiohttp


async def send_discord(settings, notification):
    '''
    Call this to send a Discord message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: Recipient information and message keys
    '''
    if settings.SEND_DISCORD is True:
        logging.warning(f"Simulating sending Discord message: '{notification.get('message')}'.")
