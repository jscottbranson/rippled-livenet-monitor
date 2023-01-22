'''
Send messages via Slack webhook.
'''
import logging
import asyncio

import aiohttp


async def send_slack(settings, notification):
    '''
    Call this to send a Slack message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: recipient information and message text
    '''
    if settings.SEND_SLACK is True:
        logging.warning(f"Simulating sending Slack message: '{notification.get('message')}'.")
