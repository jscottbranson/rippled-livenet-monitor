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
        logging.error(f"Error determining SSL/TLS settings for server: {server}")
        return None

async def websocket_subscribe(server, subscription_command, message_queue):
    '''
    Connect to a websocket address using TLS settings specified in 'url'.
    Keep the socket open, and add unique response messages from the remote server to
    the queue.

    :param dict server: URL and SSL certificate verification settings
    :param json subscription_command: JSON object to send after opening the connection
    :param asyncio.queues.Queue message_queue: Queue for incoming websocket messages
    '''

    try:
        # Check to see if a custom SSLContext is needed to ignore cert verification
        # Establish a connection object
        logging.info(f"Attempting to connect to: {server['url']}.")
        websocket_connection = await create_ws_object(server)
    except (websockets.exceptions.InvalidURI) as error:
        websocket_connection = None
        logging.critical(f"Unable to connect to server: {server}; due to error: {error}")

    if websocket_connection is not None:
        try:
            async with websocket_connection as ws:
                # Subscribe to the websocket stream
                await ws.send(json.dumps(subscription_command))
                logging.warning(f"Subscribed to: {server['url']}")
                while True:
                    # Listen for response messages
                    data = await ws.recv()
                    try:
                        data = json.loads(data)
                        await message_queue.put(
                            {"server_url": server['url'], "data": data}
                        )
                    except (json.JSONDecodeError,) as error:
                        logging.warning(f"{server['url']}. Unable to decode JSON: {data}. Error: {error}")
                    except (KeyboardInterrupt, RuntimeError):
                        await ws.close()
        except (
            asyncio.exceptions.TimeoutError,
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
            logging.warning(f"An exception: ({error}) resulted in the websocket connection to: {server['url']} being closed.")
            await websocket_connection.close()
        except () as error:
            logging.warning(f"Connection to {server['url']} refused with error: {error}.")
            await websocket_connection.close()
