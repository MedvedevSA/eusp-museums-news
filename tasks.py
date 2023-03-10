import asyncio

from celery import Celery
from celery.utils.log import get_task_logger

from wp_parser import WPParser
from config import settings

celery = Celery("worker", broker=f"redis://{settings.REDIS_HOST}:6379/0")
logger = get_task_logger(__name__)


@celery.task()
def wp_parser_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(WPParser(log=logger).run())