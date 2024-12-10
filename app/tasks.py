from celery import shared_task
from celery.contrib.abortable import AbortableTask

from time import sleep

from datetime import datetime

# tutorial 2

@shared_task()
def hello_world():
    for i in range(1, 6):
        print(i)
        sleep(1)
    print("Hello Celery")

@shared_task()
def twenty_seconds():
    print("Running every 20 seconds!")
