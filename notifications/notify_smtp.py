'''
Send messages via Email.
'''
import logging
import asyncio
from aiosmtplib import send
from email.message import EmailMessage

async def send_message(settings, email_message):
    '''
    Send the SMTP notification.
    '''
    await send(
            email_message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_SUBMISSION_PORT,
            start_tls=settings.SMTP_START_TLS,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            )
    
async def compile_email(settings, message_body, recipient):
    '''
    Add 'from', 'to', and 'subject'.
    '''
    email_message = EmailMessage()
    email_message['From'] = settings.SMTP_USERNAME
    email_message['To'] = recipient['smtp_to']
    email_message['Subject'] = recipient['smtp_subject']
    email_message.set_content(message_body)

    return email_message

async def send_email(settings, notification):
    '''
    Prepare and send notification emails.
    '''
    email_settings = notification.get('server').get('notifications').get('smtp')
    message_body = notification.get('message')
    response = []

    if email_settings and message_body:
        for recipient in email_settings.get('smtp_recipients'):
            logging.info(f"preparing to send smtp message to: {recipient}.\n{message_body}\n\n")
            email_message = await compile_email(settings, message_body, recipient)
            await send_message(settings, email_message)

async def send_smtp(settings, notification):
    '''
    Call this to send a Email message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: Notification message and contact information.
    '''
    if settings.SEND_SMTP is True:
        logging.info(f"Sending Email message: '{notification.get('message')}'.")
        smtp_responses = await send_email(settings, notification)
    else:
        logging.info(f"SMTP notifications disabled in settings. Ignoring: '{notification}'.")
