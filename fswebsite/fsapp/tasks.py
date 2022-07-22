from __future__ import absolute_import, unicode_literals
from celery import Celery, shared_task
import time
import random
from celery.utils.log import get_task_logger

app = Celery('fswebsite', backend='redis://localhost', broker='redis://localhost:6379/0')
app.autodiscover_tasks()
logger = get_task_logger(__name__)

@shared_task(ignore_result=False)
def add(x, y):
    num1 = random.randint(5, 20)
    time.sleep(num1)
    result = x + y
    logger.info(f'Add: {x} + {y} = {result}')
    return x + y