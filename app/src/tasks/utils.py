import logging
import time
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)


def task_with_wait_time(func):

    @wraps(func)
    def wrapper(*args, wait_time: int = None, **kwargs):
        now = datetime.now().isoformat()
        logger.info('----------------------------')
        logger.info(
            f'Processing task at {now} {func.__name__}({args}, wait_time={wait_time}, {kwargs})',
        )
        logger.info('----------------------------')
        if wait_time:
            for i in range(wait_time):
                logger.debug(f'Waiting 1 sec ({i}/{wait_time} step)')
                time.sleep(1)
        result = func(*args, **kwargs)
        logger.info('***********************************')
        logger.info(f'DONE {func.__name__} received at {now}, result={result}')
        logger.info('***********************************')
        return result

    return wrapper
