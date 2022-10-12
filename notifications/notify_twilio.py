import os
import logging
import asyncio
import twilio
from twilio.rest import Client


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
    except KeyError as error:
        logging.critical(f"Unable to locate Twilio auth credentials. Error: {error}.")

    return sid, auth_token

async def send_twilio_sms(settings, message_body):
    '''
    Send a SMS message.
    :param settings: Config file
    :param str message_body: Message content
    '''
    sid, auth_token = await get_account_info(settings)

    # Remove extraneous characters from phone numbers
    number_from = ''.join(x for x in settings.NUMBER_FROM if x.isdigit() or x == "+")
    number_to = ''.join(x for x in settings.NUMBER_TO if x.isdigit() or x == "+")

    # Send the message
    try:
        client = Client(sid, auth_token)

        if sid and auth_token:
            message = client.messages.create(
                body=message_body,
                from_=number_from,
                to=number_to
            )
        return(message.sid)

    except twilio.base.exceptions.TwilioException as error:
        logging.critical(f"Error sending Twilio SMS: {error}")
