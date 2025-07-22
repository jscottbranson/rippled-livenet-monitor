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
    discord_settings = notification.get('server').get('notifications').get('discord')
    message = {'content': str(notification.get('message'))}
    responses = []

    if discord_settings and message:
        for server in discord_settings.get('discord_servers'):
            discord_url = f"{settings.DISCORD_WEBHOOK_URL}{server.get('discord_id')}/{server.get('discord_token')}"

            logging.info("Preparing to send Discord message: '%s'.", message)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        discord_url,
                        headers={'Content-Type': 'application/json'},
                        json=message,
                    ) as response:
                        responses.append(response)
            except (
                ValueError,
                OSError,
                socket.gaierror,
            ) as error:
                logging.error(
                    "Error sending Discord message: '%s'.", error
                )
                # It probably makes sense to retry sending the message here.

    return responses

async def rate_limit(settings, notification, response):
    '''
    Deal with Discord rate limiting.
    '''
    logging.warning("Exceeded Discord's rate limit: '%s'.", response)
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
        logging.warning(
            "Error code encountered when sending to  Discord: '%s'.", response
        )
        # Call a function to deal with other error codes

async def send_discord(settings, notification):
    '''
    Call this to send a Discord message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: Recipient information and message keys
    '''
    server_responses = await discord_post(settings, notification)
    for response in server_responses:
        await discord_response(settings, notification, response)
