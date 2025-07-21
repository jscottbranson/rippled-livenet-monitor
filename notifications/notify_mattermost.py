'''
Send notifications via Mattermost webhook.
'''
import logging
import socket

import aiohttp

async def mattermost_post(notification):
    '''
    Use aiohttp to POST message to a Mattermost webhook.

    :param dict notification: Recipient information and message keys.
    '''
    mm_settings = notification.get('server').get('notifications').get('mattermost')
    message = {'text': str(notification.get('message'))}
    responses = []

    logging.info("Preparing to send Mattermost message: '%s'.", message)

    if mm_settings and message:
        for server in mm_settings.get('mattermost_servers'):
            if server.get('mattermost_url') and server.get('mattermost_key'):
                mm_url = f"{server.get('mattermost_url')}/hooks/{server.get('mattermost_key')}"
                # Per MM documentation, specifying a channel is optional.
                # If channel is not specified, messages go in the default channel
                # assigned to the bot in MM settings.
                if server.get('mattermost_channel'):
                    message['channel'] = server['mattermost_channel']

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            mm_url,
                            headers={'Content-Type': 'application/json'},
                            json=message,
                        ) as response:
                            responses.append(response)

                except (
                    ValueError,
                    OSError,
                    socket.gaierror,
                ) as error:
                    logging.error("Error sending Mattermost message: '%s'.", error)
    return responses

async def mattermost_response(settings, notification, response):
    '''
    Ensure MM messages sent successfully.
    '''
    if int(response.status) not in [200, 204]:
        logging.warning("Error response encountered when sending to Mattermost: '%s'.", response)
        # Call a function to deal with error codes

async def send_mattermost(settings, notification):
    '''
    Call this to send a Mattermost message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: recipient information and message text
    '''
    if settings.SEND_MATTERMOST is True:
        server_responses = await mattermost_post(notification)
        for response in server_responses:
            await mattermost_response(settings, notification, response)
    else:
        logging.info("Mattermost notifications disabled in settings. Ignoring: '%s'.", notification)
