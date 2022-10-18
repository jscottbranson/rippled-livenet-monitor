import os
import logging
import asyncio

import requests

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

async def send_message(sid, auth_token, number_from, number_to, message_body):
    '''
    Use the prepared information to send the message.

    :parm str sid: Twilio client ID
    :param str auth_token: Twilio authentication token
    :param str number_from: Number to send from
    :param str number_to: Recipient's SMS number
    :param str message_body: Message content
    '''
    try:
        client = Client(sid, auth_token)

        message = client.messages.create(
            body=message_body,
            from_=number_from,
            to=number_to
        )
        return message.sid

    except (
        twilio.base.exceptions.TwilioException,
        requests.exceptions.ConnectionError,
    ) as error:
        logging.critical(f"Error sending Twilio SMS: {error}")

async def clean_number(number):
    '''
    Clean a phone number.

    :param str number: Phone number to be cleaned.
    '''
    number_clean = ''.join(x for x in number if x.isdigit() or x == "+")
    logging.info(f"Successfully cleaned SMS number: {number}. Result: {number_clean}.")
    return number_clean

async def prep_send_message(settings):
    '''
    Send the SMS Message.

    :param settings: Config file
    '''
    # Get authentication information
    sid, auth_token = await get_account_info(settings)

    # Remove extraneous characters from phone numbers
    number_from = await clean_number(settings.NUMBER_FROM)
    number_to = await clean_number(settings.NUMBER_TO)

    return sid, auth_token, number_from, number_to

async def send_twilio_sms(settings, message_body):
    '''
    Call this to send a SMS message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param str message_body: Message content
    '''

    sid, auth_token, number_from, number_to = await prep_send_message(settings)
    sms_response = await send_message(sid, auth_token, number_from, number_to, message_body)
    logging.info(f"Successfully sent SMS message: {message_body}. Received response {sms_response}.")
    return sms_response
