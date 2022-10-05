'''
Run the program.
'''
import logging
import settings
from server_subscription.subscribe_server import start_server_info

def set_logging():
    '''
    Set logging params.
    '''
    logging.basicConfig(
        filename="monitor.log",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
    )

if __name__ == '__main__':
    set_logging()
    start_server_info(settings)
