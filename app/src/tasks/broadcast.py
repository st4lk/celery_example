from celery_app import app
from .utils import task_with_wait_time


@app.task
@task_with_wait_time
def broadcast_task():
    return 'Success broadcast_task'
