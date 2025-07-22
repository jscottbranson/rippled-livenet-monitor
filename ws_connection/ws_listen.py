'''
Listen for incoming websocket messages.
'''
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
    if server.get('ssl_verify') is False and server['url'][0:4].lower() == 'wss:':
        ssl_context = ssl.SSLContext()
        ssl_context.verify_mode = ssl.CERT_NONE
        connection = websockets.connect(server.get('url'), ssl=ssl_context)
    elif server['ssl_verify'] is True or server['url'][0:3].lower() == 'ws:':
        connection = websockets.connect(server.get('url'))
    else:
        logging.error("Error determining SSL/TLS settings for server: '%s'.", server)
        connection = None
    return connection

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
        logging.info("Attempting to connect to: '%s'.", server.get('server_name'))
        async with await create_ws_object(server) as ws:
            await ws.send(json.dumps(server['command']))
            logging.warning(
                "Subscribed to: '%s' with command: '%s'.",
                server.get('server_name'), server.get('command')
            )
            while True:
                # Listen for response messages
                try:
                    data = await ws.recv()
                    data = json.loads(data)
                    message_queue.put(
                        {"server_url": server.get('url'), "data": data}
                    )
                except (json.JSONDecodeError,) as error:
                    logging.warning(
                        "Server: '%s'. Unable to decode JSON: '%s'. Error: '%s'.",
                        server.get('server_name'), data, error
                    )
                except (asyncio.CancelledError, KeyboardInterrupt):
                    logging.warning(
                        "Keyboard Interrupt detected. Closing websocket connection to: '%s'.", server
                    )
                    await ws.close()
                    break
    except (
        asyncio.exceptions.TimeoutError,
        asyncio.exceptions.CancelledError,
        OSError,
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
        logging.warning(
            "An exception: '%s' resulted in the websocket connection to: '%s' being closed.",
            error, server.get('server_name')
        )
    except (
        websockets.exceptions.InvalidURI,
    ) as error:
        websocket_connection = None
        logging.critical(
            "Unable to connect to server: '%s' due to an invalid URI: '%s'.", server, error
        )
