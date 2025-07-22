'''
Send messages via Email.
'''
import logging
from email.message import EmailMessage
from aiosmtplib import send

async def send_message(settings, email_message):
    '''
    Send the SMTP notification.
    '''
    try:
        status, response = await send(
                email_message,
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_SUBMISSION_PORT,
                start_tls=settings.SMTP_START_TLS,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                )
        return status, response
    except Exception as e:
        return None, f"Python3 error sending mail: {e}"

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
    smtp_responses = []

    if email_settings and message_body:
        for recipient in email_settings.get('smtp_recipients'):
            logging.info(
                "Preparing to send SMTP message to: '%s'. Message:\n '%s'\n\n",
                recipient, message_body
            )
            email_message = await compile_email(settings, message_body, recipient)
            status, response = await send_message(settings, email_message)
            smtp_responses.append({'status': status, 'response': response})
    return smtp_responses

async def process_response(settings, notification, response):
    '''
    Error handling.
    '''
    if response.get('status')[0] == 2:
        logging.info("Successfully sent SMTP notification: %s %s", notification, response)
    elif response.get('status')[0] == 5:
        # Do not attempt to resend SMTP messages after a 5xx response code is received.
        logging.warning(
            "Error sending SMTP notification. \
            Resending will not be attempted due to 5xx error code. \
            Notification: '%s' Response: '%s'", notification, response
        )
    else:
        logging.warning(
            "Error sending SMTP notification. Resending should be attempted. \
            Notification: '%s' Response: '%s'", notification, response
        )

async def send_smtp(settings, notification):
    '''
    Call this to send a Email message.
    This function is not responsible for sending the message

    :param settings: Config file
    :param dict notification: Notification message and contact information.
    '''
    logging.info(
        "Sending Email message: '%s'.", notification.get('message')
    )
    # Add response error handling
    smtp_responses = await send_email(settings, notification)
    #for response in smtp_responses:
    #    await process_response(settings, notification, response)
