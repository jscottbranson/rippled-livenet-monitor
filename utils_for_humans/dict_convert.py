'''
Create validator and stock server dictionaries.
This tool is designed to convert more basic old style settings dictionaries
into newer dictionaries. It is also useful for updating notification settings for multiple servers
at once.

You can `cat settings_new.py >> settings.py` after
setting variables and running this script.
'''
import json
import to_monitor as settings

# Change the following variables as needed:
OUTPUT_FILE = 'settings_new.py'

NOTIFY_TWILIO = False
NOTIFY_DISCORD = False
NOTIFY_MATTERMOST = True
NOTIFY_SLACK = False
NOTIFY_SMTP = False

PHONE_FROM = "+10000000"
PHONE_TO = "+10000000"

DISCORD_ID = ""
DISCORD_TOKEN = ""

MATTERMOST_URL = "https://example.com"
MATTERMOST_KEY = "foo"
MATTERMOST_CHANNEL = "@bazz"

NOTIFICATION_DICT = {
    "notifications": {
        "twilio": {
            "notify_twilio": None,
            "phone_numbers": [
                {
                    "phone_from": None,
                    "phone_to": None,
                },
            ],
        },
        "discord": {
            "notify_discord": None,
            "discord_servers": [
                {
                    "discord_id": None,
                    "discord_token": None,
                },
            ],
        },
        "mattermost": {
            "notify_mattermost": None,
            "mattermost_servers": [
                {
                    "mattermost_url": None,
                    "mattermost_key": None,
                    "mattermost_channel": None,
                },
            ],
        },
        "slack": {
            "notify_slack": None,
        },
        "smtp": {
            "notify_smtp": None,
        }
    },
}

# Don't change things below here
def output_text(servers, validators):
    '''
    Write the server and validator lists to a text file with the
    appropriate variable names.

    :param list servers: servers
    :param list validators: validators
    '''
    SERVERS = str(servers)
    VALIDATORS = str(validators)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        file.write("SERVERS = ")
        file.write(SERVERS)
        file.write("\n\nVALIDATORS = ")
        file.write(VALIDATORS)

def build_servers(servers):
    '''
    Construct a list of dicts for each stock server.

    :param dict servers: url, server_name, ssl_verify for each server.
    '''
    new_servers = []
    for server in servers:
        new_servers.append(
            {
                'server_name': server.get('server_name'),
                'url': server.get('url'),
                'ssl_verify': server.get('ssl_verify'),
                'notifications': NOTIFICATION_DICT['notifications'],
            }
        )
    return new_servers

def build_validators(validators):
    '''
    Construct a list of dicts for each validator.

    :param dict validators: , server_name and master_key or validation_public_key for each server.
    '''
    new_validators = []
    for validator in validators:
        new_validators.append(
            {
                'server_name': validator.get('server_name'),
                'master_key': validator.get('master_key'),
                'validation_public_key': validator.get('validation_public_key'),
                'notifications': NOTIFICATION_DICT['notifications'],
            }
        )
    return new_validators

def build_notification_dict():
    '''
    Translate variables into a model notification dict.
    '''
    # Isolate each notification method
    twilio = NOTIFICATION_DICT['notifications']['twilio']
    discord = NOTIFICATION_DICT['notifications']['discord']
    mattermost = NOTIFICATION_DICT['notifications']['mattermost']
    slack = NOTIFICATION_DICT['notifications']['slack']
    smtp = NOTIFICATION_DICT['notifications']['smtp']

    # Set the notification parameters
    twilio['notify_twilio'] = NOTIFY_TWILIO
    discord['notify_discord'] = NOTIFY_DISCORD
    mattermost['notify_mattermost'] = NOTIFY_MATTERMOST
    slack['notify_slack'] = NOTIFY_SLACK
    smtp['notify_smtp'] = NOTIFY_SMTP

    # Set Twilio numbers
    twilio['phone_numbers'][0]['phone_from'] = PHONE_FROM
    twilio['phone_numbers'][0]['phone_to'] = PHONE_TO

    # Set Discord server info
    discord['discord_servers'][0]['discord_id'] = DISCORD_ID
    discord['discord_servers'][0]['discord_token'] = DISCORD_TOKEN

    # Set MM server info
    mattermost['mattermost_servers'][0]['mattermost_url'] = MATTERMOST_URL
    mattermost['mattermost_servers'][0]['mattermost_key'] = MATTERMOST_KEY
    mattermost['mattermost_servers'][0]['mattermost_channel'] = MATTERMOST_CHANNEL

if __name__ == '__main__':
    build_notification_dict()
    servers_new = build_servers(settings.SERVERS)
    validators_new = build_validators(settings.VALIDATORS)
    output_text(servers_new, validators_new)
