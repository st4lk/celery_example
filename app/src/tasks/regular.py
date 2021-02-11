import logging

from celery_app import app
from .utils import task_with_wait_time

logger = logging.getLogger(__name__)


class UnpickableException(Exception):

    def __init__(self, custom_arg):
        self.custom_arg = custom_arg


class PickableException(Exception):

    def __init__(self, custom_arg, **kwargs):
        self.custom_arg = custom_arg
        print(f'I have custom_arg: {custom_arg} and kwargs: {kwargs}')
        super().__init__(custom_arg)


@app.task
@task_with_wait_time
def simple_task(*args, **kwargs):
    return 'Success simple_task'


@app.task
@task_with_wait_time
def second_simple_task(*args, **kwargs):
    return 'Success second_simple_task'


# @app.task(rate_limit='1/m')
@app.task(rate_limit='1/h')
@task_with_wait_time
def rate_limited_task(*args, **kwargs):
    return 'Success rate_limited_task'


@app.task
@task_with_wait_time
def task_with_exception(*args, **kwargs):
    raise ValueError
    return 'Success task_with_exception'


@app.task(
    autoretry_for=(ValueError,),
    default_retry_delay=150,  # try 150 - with visibility_timeout ~= 5 will result in duplication
    max_retries=2,
)
@task_with_wait_time
def task_with_exception_with_retry(*args, **kwargs):
    raise ValueError
    return 'Success task_with_exception_with_retry'


@app.task(acks_late=True, time_limit=15)
@task_with_wait_time
def acks_late_simple_task(*args, **kwargs):
    return 'Success acks_late_simple_task'


@app.task(acks_late=True)
@task_with_wait_time
def acks_late_task_with_exception(*args, **kwargs):
    raise ValueError
    return 'Success acks_late_task_with_exception'


@app.task
@task_with_wait_time
def task_with_unpickable_exception(*args, **kwargs):
    raise UnpickableException(custom_arg='Universe')


@app.task
@task_with_wait_time
def task_with_pickable_exception(*args, **kwargs):
    raise PickableException(custom_arg='Sun', something_else='Surprise')
