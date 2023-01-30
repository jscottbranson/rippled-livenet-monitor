'''
Send notifications via Mattermost webhook.
'''
import logging
import asyncio

import aiohttp


async def send_mattermost(settings, notification):
    '''
    Call this to send a Mattermost message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: recipient information and message text
    '''
    if settings.SEND_MATTERMOST is True:
        logging.warning(f"Simulating sending Mattermost message: '{notification.get('message')}'.")
    else:
        logging.info(f"Mattermost notifications disabled in settings. Ignoring: '{notification}'.")
