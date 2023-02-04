import asyncio

from celery import Celery

import wp_parser

REDIS_HOST = 'localhost'
celery = Celery("worker", broker=f"redis://{REDIS_HOST}:6379/0")

@celery.task()
def wp_parser_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wp_parser.run_parse())