import asyncio
import json
import logging
import socket
import ssl

import websockets

async def create_ws_object(server):
    '''
    Check if SSL certificate verification is enabled, then create a ws accordingly.

    :param dict server: URL and SSL certificate verification settings
    :return: A websocket connection
    '''
    if server['ssl_verify'] is False and server['url'][0:4].lower() == 'wss:':
        ssl_context = ssl.SSLContext()
        ssl_context.verify_mode = ssl.CERT_NONE
        return websockets.connect(server['url'], ssl=ssl_context)
    elif server['ssl_verify'] is True or server['url'][0:3].lower() == 'ws:':
        return websockets.connect(server['url'])
    else:
        logging.error(f"Error determining SSL/TLS settings for server: '{server}'.")
        return None

async def websocket_subscribe(server, message_queue):
    '''
    Connect to a websocket address using TLS settings specified in 'url'.
    Keep the socket open, and add unique response messages from the remote server to
    the queue.

    :param dict server: URL SSL certificate, and subscription command
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    '''

    try:
        # Check to see if a custom SSLContext is needed to ignore cert verification
        # Establish a connection object
        logging.info(f"Attempting to connect to: '{server['name']}'.")
        async with await create_ws_object(server) as ws:
            await ws.send(json.dumps(server['command']))
            logging.warning(f"Subscribed to: '{server['name']}' with command: '{server['command']}'.")
            while True:
                # Listen for response messages
                try:
                    data = await ws.recv()
                    data = json.loads(data)
                    await message_queue.put(
                        {"server_url": server['url'], "data": data}
                    )
                except (json.JSONDecodeError,) as error:
                    logging.warning(f"Server: '{server['name']}'. Unable to decode JSON: '{data}'. Error: '{error}'.")
                except KeyboardInterrupt:
                    logging.warning(f"Keyboard Interrupt detected. Closing websocket connection to: '{server}'.")
                    await ws.close()
                    break
    except (
        asyncio.exceptions.TimeoutError,
        asyncio.exceptions.CancelledError,
        TimeoutError,
        ConnectionResetError,
        ConnectionError,
        ConnectionRefusedError,
        ssl.CertificateError,
        websockets.exceptions.InvalidStatusCode,
        websockets.exceptions.ConnectionClosedError,
        websockets.exceptions.ConnectionClosedOK,
        websockets.exceptions.InvalidMessage,
        socket.gaierror,
    ) as error:
        logging.warning(f"An exception: '{error}' resulted in the websocket connection to: '{server['name']}' being closed.")
    except (
        websockets.exceptions.InvalidURI,
    ) as error:
        websocket_connection = None
        logging.critical(f"Unable to connect to server: '{server}' due to an invalid URI: '{error}'.")
