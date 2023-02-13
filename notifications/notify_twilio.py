import os
import logging
import socket
import asyncio

import aiohttp


async def get_account_info(settings):
    '''
    Locate the Twilio SID and auth_token either in settings.py or as
    env variables.
    :param settings: Configuration file
    '''
    sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    try:
        if not settings.TWILIO_ACCOUNT_SID:
            sid = os.environ['TWILIO_ACCOUNT_SID']
        if not settings.TWILIO_AUTH_TOKEN:
            auth_token = os.environ['TWILIO_AUTH_TOKEN']
        logging.info("Successfully located Twilio auth credentials.")
    except KeyError as error:
        logging.critical(f"Unable to locate Twilio auth credentials. Error: {error}.")

    return sid, auth_token

async def send_message(sid, auth_token, phone_from, phone_to, message_body):
    '''
    Use the prepared information to send the message.

    :parm str sid: Twilio client ID
    :param str auth_token: Twilio authentication token
    :param str phone_from: Number to send from
    :param str phone_to: Recipient's SMS number
    :param str message_body: Message content
    '''
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(
            login=sid, password=auth_token)) as session:
            return await session.post(
                # This URL prob shouldn't be hard coded
                f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json',
                data={'From': phone_from, 'To': phone_to, 'Body': message_body}
            )

    except (
        OSError,
        socket.gaierror,
    ) as error:
        # Double check these exceptions
        # Retry SMS messages that throw exceptions, if appropriate
        logging.critical(f"Error sending Twilio SMS: '{error}'.")

async def clean_number(number):
    '''
    Remove everything that isn't an integer or plus sign from a phone (SMS) number.

    :param str number: Number to clean

    :returns: Cleaned number
    :rtype: str
    '''
    return ''.join(x for x in number if x.isdigit() or x == "+")

async def send_twilio(settings, notification):
    '''
    Call this to send a SMS message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: phone_from, phone_to, and message keys
    '''
    if settings.SEND_TWILIO is True:
        sid, auth_token = await get_account_info(settings)

        twilio_settings = notification['server']['notifications']['twilio']
        for i in twilio_settings.get('phone_numbers'):
            phone_from = await clean_number(i['phone_from'])
            phone_to = await clean_number(i['phone_to'])

            logging.info(f"Preparing to send SMS message: '{notification}'.")
            sms_response = await send_message(
                sid, auth_token, phone_from, phone_to, notification['message']
            )
            logging.info(f"Successfully sent SMS message: {notification['message']}. Received response {sms_response}.")

    else:
        logging.info(f"Twilio messages disabled in settings. Ignored SMS message: '{notification}'.")
