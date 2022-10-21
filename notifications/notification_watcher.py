'''
Watch for incoming SMS notification messages and deal with them accordingly.

Notifications should be sent here to be dispatched, not to individual messaging services.
'''
import logging
import asyncio

from .notify_twilio import send_twilio_sms

async def notifications(settings, sms_queue):
    '''
    Watch for incoming notifications.
    '''
    logging.info("Notification watcher is running.")
    while True:
        try:
            message = await sms_queue.get()
            if settings.TWILIO is True:
                response_twilio = await send_twilio_sms(settings, message)
        except KeyboardInterrupt:
            logging.warning("Keyboard interrupt detected. Stopping notification watcher.")
            break
