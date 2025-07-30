'''
Send notifications via Mattermost webhook.
'''
import logging
import socket

import copy
import asyncio
import aiohttp

async def post_to_mattermost(settings, mm_url, message, retry_counter=0, retry_sleep_time=None):
    '''
    Send a POST request to a specified MatterMost server.
    '''
    retry = None

    if retry_sleep_time is None:
        retry_sleep_time = int(settings.NOTIFY_RETRY_SLEEP_TIME)

    if retry_counter <= int(settings.NOTIFY_RETRY_MAX):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    mm_url,
                    headers={'Content-Type': 'application/json'},
                    json=message,
                ) as response:
                    if int(response.status) not in [200, 204]:
                        logging.error(
                            "Error code: '%i' returned when sending to Mattermost URL: '%s'.",
                            int(response.status), mm_url
                        )
                        retry = True
                    else:
                        retry = False
        except ValueError as error:
            logging.error(
                "'ValueError' when sending HTTP POST to MatterMost server: '%s'. "
                "Resending will not be reattempted.", error
            )
            retry = False
        except (
            OSError,
            socket.gaierror,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ) as error:
            logging.error("Error sending Mattermost message: '%s'.", error)
            retry = True

    if retry is True:
        logging.error(
            "Error sending MatterMost notification to: %s. "
            "Retry count: %d. Sleeping for: '%d' seconds.",
            mm_url, retry_counter, retry_sleep_time
        )
        await asyncio.sleep(retry_sleep_time)
        retry_counter +=1
        retry_sleep_time = retry_sleep_time * 2
        await post_to_mattermost(settings, mm_url, message, retry_counter, retry_sleep_time)

async def send_mattermost(settings, notification):
    '''
    Call this to POST a Mattermost message via webhook.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: recipient information and message text
    '''
    tasks = []
    mm_settings = notification.get('server').get('notifications').get('mattermost')
    message = {'text': str(notification.get('message'))}

    logging.info("Preparing to send Mattermost message: '%s'.", message)

    if mm_settings and message.get('text'):
        for server in mm_settings.get('mattermost_servers'):
            if server.get('mattermost_url') and server.get('mattermost_key'):
                mm_url = f"{server.get('mattermost_url')}/hooks/{server.get('mattermost_key')}"
                # Per MM documentation, specifying a channel is optional.
                # If channel is not specified, messages go into a default channel.
                if server.get('mattermost_channel'):
                    message['channel'] = server['mattermost_channel']
                tasks.append(
                    asyncio.create_task(
                        post_to_mattermost(settings, "".join(mm_url), copy.deepcopy(message))
                    )
                )
            else:
                logging.info(
                    "MatterMost message ignored as server URL and API Key are not specified. \
                    Message:\n%s\nServer:\n%s", message, server
                )
    if tasks:
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except KeyboardInterrupt:
            pass
