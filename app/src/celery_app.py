import os

from celery import Celery
from kombu import Queue
from kombu.common import Broadcast

import settings  # NOQA

CELERY_BROKER_NAME = os.getenv('CELERY_BROKER_NAME', 'redis')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB', '0')

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')
RABBITMQ_DEFAULT_USER = os.getenv('RABBITMQ_DEFAULT_USER')
RABBITMQ_DEFAULT_PASS = os.getenv('RABBITMQ_DEFAULT_PASS')
RABBITMQ_DEFAULT_VHOST = os.getenv('RABBITMQ_DEFAULT_VHOST')

CELERY_BROKER = None

if CELERY_BROKER_NAME == 'redis':
    CELERY_BROKER = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
elif CELERY_BROKER_NAME == 'rabbitmq':
    # RMQ_CRED = f'{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}'
    # CELERY_BROKER = 'amqp://{RMQ_CRED}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_HOSTNAME}'
    CELERY_BROKER = 'amqp://{user}:{pwd}@{host}:{port}/{vhost}'.format(
        user=RABBITMQ_DEFAULT_USER,
        pwd=RABBITMQ_DEFAULT_PASS,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        vhost=RABBITMQ_DEFAULT_VHOST,
    )
else:
    raise NotImplementedError(f'Support for {CELERY_BROKER_NAME} broker is not implemented') 

print('Broker is:', CELERY_BROKER)

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
    broker=CELERY_BROKER,
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

# periodic tasks
app.conf.beat_schedule = {
    '5-seconds': {
        'task': 'tasks.regular.simple_task',
        'schedule': 5.0,
        # 'args': (16, 16),
        'kwargs': {'wait_time': 10},
    },
}
