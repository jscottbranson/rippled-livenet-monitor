'''
Send messages via Discord webhook.

This needs support for rate limiting and other fancy stuff.
'''
import logging
import socket
import asyncio

import aiohttp

async def discord_post(settings, notification):
    '''
    Use aiohttp to POST message to Discord webhook.

    :param settings: Config file
    :param dict notification: Recipient information and message keys.
    '''
    message = {'content': str(notification.get('message'))}
    discord_settings = notification.get('server').get('notifications').get('discord')
    discord_url = f"{settings.DISCORD_WEBHOOK_URL}{discord_settings.get('discord_id')}/{discord_settings.get('discord_token')}"

    logging.info(f"Preparing to send Discord message: '{message}'.")

    if discord_settings and message:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    discord_url,
                    headers={'Content-Type': 'application/json'},
                    json=message,
                ) as response:
                    return response
        except (
            ValueError,
            OSError,
            socket.gaierror,
        ) as error:
            logging.error(f"Error sending Discord message: '{error}'.")
            # It probably makes sense to retry sending the message here.

async def rate_limit(settings, notification, response):
    '''
    Deal with Discord rate limiting.
    '''
    logging.warning(f"Discord's rate limit exceeded: '{response}'.")
    await asyncio.sleep(float(response.headers.get('retry-after')) + 0.25)
    await discord_post(settings, notification)

async def discord_response(settings, notification, response):
    '''
    Ensure discord messages are posted successfully.
    '''
    if int(response.status) in [200, 204]:
        logging.info("Discord message posted successfully.")
    elif int(response.status) == 429:
        await rate_limit(settings, notification, response)
    else:
        logging.warning(f"Error code encountered when sending to  Discord: '{response}'.")
        # Call a function to deal with other error codes

async def send_discord(settings, notification):
    '''
    Call this to send a Discord message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: Recipient information and message keys
    '''
    if settings.SEND_DISCORD is True:
        server_response = await discord_post(settings, notification)
        await discord_response(settings, notification, server_response)
    else:
        logging.warning(f"Discord notifications are disabled in settings. Ignoring message: '{notification}'.")
