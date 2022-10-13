'''
Attempt to reconnect when a websocket connection drops.
'''
import asyncio
import logging

from .ws_listen import websocket_subscribe
from notifications import notify_twilio

async def resubscribe_client(settings, ws_servers, subscription_command, server_del, message_queue):
    '''
    Attempt to reconnect dropped websocket connections to remote servers.

    :param settings: Config file
    :param list ws_servers: Connections to websocket servers
    :param dict server_del: Info on the server that the reconnection attempt will be made to
    :param dict subscription_command: Message to send to websocket server
    :param asyncio.queues.Queue queue_receive: Queue for incoming websocket messages
    :return: Connections to websocket servers
    :rtype: list
    '''
    message_body = str(f"WS connection to {server_del['name']} closed. Attempting to reconnect. Retry counter: {server_del['retry_count']}")
    logging.warning(message_body)
    if settings.TWILIO is True:
        response_id = await notify_twilio.send_twilio_sms(settings, message_body)

    server_add = \
        {
            #'task': asyncio.create_task(
            'task': asyncio.ensure_future(
                websocket_subscribe(server_del, subscription_command, message_queue)
            ),
            'url': server_del['url'],
            'name': server_del['name'],
            'ssl_verify': server_del['ssl_verify'],
            'retry_count': server_del['retry_count'] + 1,
        }

    message_body = str(f"It appears we reconnected to {server_del['name']}. Retry counter: {server_del['retry_count'] + 1}")
    logging.warning(message_body)
    if settings.TWILIO is True:
        response_id = await notify_twilio.send_twilio_sms(settings, message_body)

    return server_del, server_add

async def mind_tasks(settings, ws_servers, subscription_command, message_queue):
    '''
    Check task loop & restart websocket clients if needed.

    :param settings: The settings file
    :param list ws_servers: Connections to websocket servers
    :param dict subscription_command: Message to send to websocket server
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    '''
    while True:
        ws_servers_del = []
        ws_servers_add = []
        try:
            await asyncio.sleep(settings.WS_RETRY)
            for server in ws_servers:
                if server['task'].done() and server['retry_count'] <= settings.MAX_CONNECT_ATTEMPTS:
                    ws_del, ws_add = await resubscribe_client(
                            settings,
                            ws_servers,
                            subscription_command,
                            server,
                            message_queue
                    )
                    ws_servers_del.append(ws_del)
                    ws_servers_add.append(ws_add)
            for server in ws_servers_del:
                ws_servers.remove(server)
                logging.warning(f"Removed disconnected server from task loop: {server}.")
            for server in ws_servers_add:
                ws_servers.append(server)
                logging.warning(f"Added new connection to the task loop: {server}.")
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Stopping ws_minder.")
            break
