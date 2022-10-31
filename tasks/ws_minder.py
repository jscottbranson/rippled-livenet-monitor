'''
Monitor multiple websocket connections and attempt to reconnect when a websocket connection drops.
'''
import asyncio
import logging

from ws_connection.ws_listen import websocket_subscribe
from notifications import notify_twilio

async def queue_state_change(server_del, message_queue):
    '''
    Place a message into the queue to inform that a server is disconnected.

    :param dict server_del: Info on the server that the reconnection attempt will be made to
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    '''
    await message_queue.put(
        {
            'server_url': server_del.get('url'),
            'data': {
                'result': {
                    'server_status': 'disconnected from monitoring',
                },
            },
        }
    )

    logging.info(f"Put updated state for server: '{server_del.get('name')}' into message processing queue.")

async def generate_new_server(server_del):
    '''
    Create an object for the new connection.

    :param dict server_del: The server that will be deleted
    '''
    server_add = \
        {
            'task': None,
            'url': server_del['url'],
            'name': server_del['name'],
            'phone_from': server_del['phone_from'],
            'phone_to': server_del['phone_to'],
            'command': server_del['command'],
            'ssl_verify': server_del['ssl_verify'],
            'retry_count': server_del['retry_count'] + 1,
        }

    logging.info("Created new server connection object.")
    return server_add

async def resubscribe_client(server_del, message_queue):
    '''
    Attempt to reconnect dropped websocket connections to remote servers.

    :param dict server_del: Info on the server that the reconnection attempt will be made to
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    :return: A new server object with an active websocket connection
    :rtype: dict
    '''
    logging.info(f"WS connection to '{server_del['name']}' closed. Attempting to reconnect. Retry counter: '{server_del['retry_count']}'.")
    loop = asyncio.get_event_loop()

    # Pass a message to the queue indicating the server is disconnected
    await queue_state_change(server_del, message_queue)
    # Delete the disconnected server's task
    del server_del['task']
    # Prepare the new connection
    server_add = await generate_new_server(server_del)
    # Open the new connection
    server_add['task'] = loop.create_task(websocket_subscribe(server_del, message_queue))

    logging.info(f"It appears we reconnected to '{server_del.get('name')}'. Retry counter: '{server_del['retry_count'] + 1}'.")
    return server_add

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
                if server['task'].done() and server['retry_count'] <= settings.MAX_CONNECT_ATTEMPTS:
                    ws_add = await resubscribe_client(server, message_queue)
                    ws_servers_del.append(server)
                    ws_servers_add.append(ws_add)
            for server in ws_servers_del:
                ws_servers.remove(server)
                logging.info(f"Removed disconnected server from task loop: '{server}'.")
            for server in ws_servers_add:
                ws_servers.append(server)
                logging.info(f"Added new connection to the task loop: '{server}'.")
        except KeyboardInterrupt:
            await message_queue.join()
            logging.warning("Keyboard interrupt detected. Stopping ws_minder.")
            break
        except Exception as error:
            logging.critical(f"An otherwise uncaught exception occurred in the ws_minder: '{error}'.")
