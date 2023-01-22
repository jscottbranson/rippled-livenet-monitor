'''
Send messages via Email.
'''
import logging
import asyncio


async def send_smtp(settings, notification):
    '''
    Call this to send a Email message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: Notification message and contact information.
    '''
    if settings.SEND_SMTP is True:
        logging.warning(f"Simulating sending Email message: '{notification.get('message')}'.")
