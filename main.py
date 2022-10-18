'''
Run the program.
'''
import logging
import settings
from tasks.task_minder import start_task_loop

def set_logging():
    '''
    Set logging params.
    '''
    logging.basicConfig(
        filename=settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        datefmt="%Y-%m-%d %H:%M:%S",
        format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
    )

if __name__ == '__main__':
    set_logging()
    start_task_loop(settings)
