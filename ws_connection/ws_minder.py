'''
Monitor multiple websocket connections and attempt to reconnect when a websocket connection drops.
'''
import asyncio
import logging

from .ws_listen import websocket_subscribe
from notifications import notify_twilio

async def queue_state_change(server, message_queue):
    '''
    Place a message into the queue to inform that a server is disconnected.

    :param dict server: Info on the server that the reconnection attempt will be made to
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    '''
    message_queue.put(
        {
            'server_url': server.get('url'),
            'data': {
                'result': {
                    'server_status': 'disconnected from monitoring',
                },
            },
        }
    )

    logging.info(f"Put updated state for server: '{server.get('server_name')}' into message processing queue.")

async def resubscribe_client(server, message_queue):
    '''
    Attempt to reconnect dropped websocket connections to remote servers.

    :param dict server: The server that the reconnection attempt will be made to
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    :return: The server object with a new websocket connection
    :rtype: dict
    '''
    logging.info(f"WS connection to '{server.get('server_name')}' closed. Attempting to reconnect. Retry counter: '{server.get('ws_retry_count')}'.")
    # Pass a message to the queue indicating the server is disconnected
    await queue_state_change(server, message_queue)
    # Delete the disconnected server's task
    del server['ws_connection_task']
    server['ws_connection_task'] = None
    server['ws_retry_count'] = server['ws_retry_count'] + 1
    # Open the new connection
    loop = asyncio.get_event_loop()
    server['ws_connection_task'] = loop.create_task(websocket_subscribe(server, message_queue))
    logging.warning(f"It appears we reconnected to '{server.get('server_name')}'. Retry counter: '{server.get('ws_retry_count')}'.")
    return server

async def mind_connections(settings, ws_servers, message_queue):
    '''
    Check task loop & restart websocket clients if needed.

    :param settings: The settings file
    :param list ws_servers: Connections to websocket servers
    :param asyncio.queues.Queue message_queue: Incoming websocket messages
    '''
    while True:
        ws_servers_del = []
        ws_servers_add = []
        try:
            await asyncio.sleep(settings.WS_RETRY)
            for server in ws_servers:
                if server['ws_connection_task'].done() and server['ws_retry_count'] <= settings.MAX_CONNECT_ATTEMPTS:
                    ws_add = await resubscribe_client(server, message_queue)
                    ws_servers_del.append(server)
                    ws_servers_add.append(ws_add)
            for server in ws_servers_del:
                ws_servers.remove(server)
                logging.info(f"Removed disconnected server from task loop: '{server}'.")
            for server in ws_servers_add:
                ws_servers.append(server)
                logging.info(f"Added new connection to the task loop: '{server}'.")
        except (asyncio.CancelledError, KeyboardInterrupt):
            logging.critical("Keyboard interrupt detected. Stopping ws_minder.")
            break
        except Exception as error:
            logging.critical(f"An otherwise uncaught exception occurred in the ws_minder: '{error}'.")
