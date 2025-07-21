'''
Send messages via Slack webhook.
'''
import logging

import aiohttp


async def send_slack(settings, notification):
    '''
    Call this to send a Slack message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: recipient information and message text
    '''
    if settings.SEND_SLACK is True:
        logging.warning("Simulating sending Slack message: '%s'.", notification.get('message'))
    else:
        logging.info("Slack notifications disabled in settings. Ignoring: '%s'.", notification)
