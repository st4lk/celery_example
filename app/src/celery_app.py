import os

from celery import Celery
from kombu import Queue
from kombu.common import Broadcast

import settings  # NOQA

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB', '0')

REDIS_BROKER = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

print('Redis broker is:', REDIS_BROKER)

task_routes = {
    'tasks.critical.critical_task': {'queue': 'critical'},
    'tasks.advanced.*': {'queue': 'advanced'},
    'tasks.broadcast.broadcast_task': {
        'queue': 'broadcast_tasks',
        'exchange': 'broadcast_tasks',
        'routing_key': 'broadcast_tasks',
    },
}

app = Celery(
    'example-redis',
    broker=REDIS_BROKER,
    # backend='amqp://',
    include=['tasks'],
 )

app.conf.task_queues = (
    Queue('dedicated'),
    Broadcast('broadcast_tasks', routing_key='broadcast_tasks'),
)

# Define result backend
# REDIS_RESULT_DB = '0'
# REDIS_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULT_DB}'
# app.conf.result_backend = REDIS_RESULT_BACKEND

# Change task events queue name (in case of Redis broker, this is a pub/sub channel)
# app.conf.event_exchange = 'my_own_celery_events'


app.conf.broker_transport_options = {
    'visibility_timeout': 10,  # in seconds
    # 'visibility_timeout': 120,  # in seconds
    'queue_order_strategy': 'priority',
}


# Optional configuration, see the application user guide.
app.conf.update(
    # result_expires=3600,
    task_default_queue='default',
    task_routes=task_routes,
    # worker_prefetch_multiplier=1,
    task_send_sent_event=True,
)
