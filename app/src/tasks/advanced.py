from celery_app import app
from .utils import task_with_wait_time


@app.task
@task_with_wait_time
def task_a_one(*args, **kwargs):
    return 'Success task_a_one'


@app.task
@task_with_wait_time
def task_a_two(*args, **kwargs):
    return 'Success task_a_two'
