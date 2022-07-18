from celery import shared_task
import time
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def add(x, y):
    time.sleep(10)
    result = x + y
    logger.info(f'Add: {x} + {y} = {result}')
    return x + y