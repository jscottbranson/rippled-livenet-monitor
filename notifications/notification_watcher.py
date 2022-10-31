'''
Watch for incoming SMS notification messages and deal with them accordingly.

Notifications should be sent here to be dispatched, not to individual messaging services.
'''
import logging
import asyncio

from .notify_twilio import send_twilio_sms

async def clean_number(number):
    '''
    Remove everything that isn't an integer or plus sign from phone numbers.

    :parma str number: Phone number to clean.
    '''
    return ''.join(x for x in number if x.isdigit() or x == "+")

async def notifications(settings, sms_queue):
    '''
    Watch for incoming notifications.

    Items placed into sms_queue should be a dict with phone_to, phone_from, & message keys.
    '''
    logging.info("Notification watcher is running.")
    while True:
        try:
            message = await sms_queue.get()
            message['phone_from'] = await clean_number(message['phone_from'])
            message['phone_to'] = await clean_number(message['phone_to'])

            if settings.TWILIO is True:
                response_twilio = await send_twilio_sms(settings, message)
                logging.info(f"Twilio response: '{response_twilio}'.")
        except (asyncio.CancelledError, KeyboardInterrupt):
            #await sms_queue.join()
            logging.critical("Keyboard interrupt detected. Stopping notification watcher.")
            break
        except Exception as error:
            logging.critical(f"An otherwise uncaught exception occurred in the notification watcher: '{error}'.")
