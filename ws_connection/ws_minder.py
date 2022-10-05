'''
Attempt to reconnect when a websocket connection drops.
'''
import asyncio
import logging

from .ws_listen import websocket_subscribe

async def resubscribe_client(ws_servers, subscription_command, server, message_queue):
    '''
    Attempt to reconnect dropped websocket connections to remote servers.

    :param list ws_servers: Connections to websocket servers
    :param dict server: Info on the server that the reconnection attempt will be made to
    :param dict subscription_command: Message to send to websocket server
    :param asyncio.queues.Queue queue_receive: Queue for incoming websocket messages
    :return: Connections to websocket servers
    :rtype: list
    '''
    logging.warning(f"WS connection to {server['url']} closed. Attempting to reconnect. Retry counter: {server['retry_count']}")
    ws_servers.append(
        {
            #'task': asyncio.create_task(
            'task': asyncio.ensure_future(
                websocket_subscribe(server, subscription_command, message_queue)
            ),
            'url': server['url'],
            'retry_count': server['retry_count'] + 1,
        }
    )
    ws_servers.remove(server)
    logging.info(f"Removed disconnected server from task loop: {server}.")
    return ws_servers

async def mind_tasks(settings, ws_servers, subscription_command, message_queue):
    '''
    Check task loop & restart websocket clients if needed.

    :param settings: The settings file
    :param list ws_servers: Connections to websocket servers
    :param dict subscription_command: Message to send to websocket server
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    '''
    while True:
        try:
            await asyncio.sleep(settings.WS_RETRY)
            for server in ws_servers:
                if server['task'].done() and server['retry_count'] <= settings.MAX_CONNECT_ATTEMPTS:
                    ws_servers = await resubscribe_client(
                        ws_servers,
                        subscription_command,
                        server,
                        message_queue
                    )
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Stopping ws_minder.")
            break
