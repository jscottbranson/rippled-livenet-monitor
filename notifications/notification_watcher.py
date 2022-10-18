'''
Watch for incoming notification messages and deal with them accordingly.
'''
import logging
import asyncio

from .notify_twilio import send_twilio_sms

async def notifications(settings, sms_queue):
    '''
    Watch for incoming notiifcations.
    '''
    logging.info("~notification watcher is running.")
    if settings.TWILIO is True:
        provider = send_twilio_sms
    while True:
        try:
            message = await sms_queue.get()
            response = await provider(settings, message)
        except KeyboardInterrupt:
            logging.warning("Keyboard interrupt detected. Stopping notification watcher.")
            break

