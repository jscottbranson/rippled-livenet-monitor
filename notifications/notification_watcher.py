'''
Watch for incoming SMS notification messages and deal with them accordingly.

Notifications should be sent here to be dispatched, not to individual messaging services.
'''
import logging
import asyncio

from .notify_twilio import send_twilio
from .notify_discord import send_discord
from .notify_slack import send_slack
from .notify_mattermost import send_mattermost
from .notify_smtp import send_smtp

async def dispatch_notification(settings, notification):
    '''
    Determine where to send the message, and dispatch it.

    :param settings: Config file
    :param dict notification: Message and notification information
    '''
    recipients = notification['server']['notifications']

    for i in settings.KNOWN_NOTIFICATIONS:
        if i in recipients.keys():
            allowed = recipients.get(str(i)).get('notify_' + str(i))

        if allowed is True:
            notification_function = "send_" + str(i)

            possibles = globals().copy()
            possibles.update(locals())
            method = possibles.get(notification_function)
            if method:
                await method(settings, notification)
            else:
                logging.warning(f"Error locating the function for notification method: '{i}'. To send notification: '{notification}'.")

async def notifications(args_d):
    '''
    Watch for incoming notifications. Messages should be a dictionary with a 'message' key and
    a 'server' key. The former should have a string with the content of the notification. The server
    field must contain the notification settings for the message recipient. The message will be
    dispatched via all enabled notification channels.

    Items placed into notification_queue should be a dict with "'server': {'notifications':{}}" &
    'message' keys.

    :param dict args_d: Default settings and queues.
    '''
    logging.info("Notification watcher is running.")
    while True:
        try:
            notification = args_d['notification_queue'].get()
            await dispatch_notification(args_d['settings'], notification)

        except (asyncio.CancelledError, KeyboardInterrupt):
            logging.critical("Keyboard interrupt detected. Stopping notification watcher.")
            break
        except Exception as error:
            logging.critical(f"An otherwise uncaught exception occurred in the notification watcher: '{error}'.")

def start_notifications(args_d):
    '''
    Start the asyncio loop.
    '''
    loop = asyncio.new_event_loop()
    monitor_tasks = []

    try:
        monitor_tasks.append(
            loop.create_task(notifications(args_d))
        )

        logging.warning("Notification loop started.")
        loop.run_forever()

    except KeyboardInterrupt:
        for task in monitor_tasks:
            task.cancel()
        logging.critical("Closed notification asyncio loops.")
