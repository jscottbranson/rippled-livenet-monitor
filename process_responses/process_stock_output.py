'''
Process server and ledger subscription messages.
This output is not relevant for monitoring validations.
'''
import logging
import time


async def update_table_ledger(table, message):
    '''
    Add information from ledger closed messages into the table.

    :param list table: Dictionary for each server being tracked
    :param dict message: Incoming ledger close message

    :rtype: list
    '''

    for server in table:
        if server['url'] == message['server_url']:
            for key in server.keys():
                if key in message['data'].keys():
                    server[key] = message['data'][key]
            server['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.gmtime())
            logging.info(
                "Successfully updated the table with ledger closed message from: '%s'.",
                server.get('url')
            )

    return table

async def check_state_change(server, message, notification_queue):
    '''
    Check if the server's state changed from the last known state.

    :param list table: Dictionary for each server being tracked (previous state information)
    :param dict message: Message with new information about the server
    :param asyncio.queues.Queue notification_queue: Outbound message queue
    '''
    if server.get('server_status') != message.get('server_status') \
       and server.get('server_status') is not None:
        now = time.strftime("%m-%d %H:%M:%S", time.gmtime())

        body = "State changed for server: "
        body = body + str(f"'{server.get('server_name')}' with key '{server.get('pubkey_node')[:5]}'. ")
        body = body + str(f"From: '{server.get('server_status')}'. ")
        body = body + str(f"To: '{message.get('server_status')}'. ")
        body = body + str(f"Time UTC: {now}.")

        logging.warning(body)
        notification_queue.put(
            {
                'message': body,
                'server': server,
            }
        )

async def update_table_server(table, notification_queue, message):
    '''
    Add info contained in new messages to the table.

    :param settings: Config file
    :param list table: Dictionary for each server being tracked
    :param asyncio.queues.Queue notification_queue: Message queue to send via SMS
    :param dict message: New server subscription message
    '''
    logging.info(
        "Server status message received '%s'. Preparing to update the table.", message
    )
    if message['data'].get('result'):
        message_result = message['data']['result']
    elif message['data'].get('type') == 'serverStatus':
        message_result = message['data']

    for server in table:
        if server['url'] == message['server_url']:
            await check_state_change(server, message_result, notification_queue)
            for key in message_result.keys():
                if key in server.keys():
                    server[key] = message_result[key]
            server['time_updated'] = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

            logging.info("Successfully updated the server status table.")

    return table
