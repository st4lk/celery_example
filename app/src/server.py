from flask import Flask, request

import settings  # NOQA
import tasks


app = Flask(__name__)


def create_chained_aka_linked_task(wait_time=1):
    signature = tasks.simple_task.si(some_param=5, wait_time=wait_time)
    signature.link(tasks.second_simple_task.si(another_param=8, wait_time=wait_time))
    return signature


TASK_MAP = {
    'simple_task': tasks.simple_task,
    'second_simple_task': tasks.second_simple_task,
    'rate_limited_task': tasks.rate_limited_task,
    'task_with_exception': tasks.task_with_exception,
    'task_with_exception_with_retry': tasks.task_with_exception_with_retry,
    'acks_late_simple_task': tasks.acks_late_simple_task,
    'acks_late_task_with_exception': tasks.acks_late_task_with_exception,
    'critical_task': tasks.critical_task,
    'task_a_one': tasks.task_a_one,
    'task_a_two': tasks.task_a_two,
    'broadcast_task': tasks.broadcast_task,
    'chained_aka_linked_task': create_chained_aka_linked_task,
    'task_with_unpickable_exception': tasks.task_with_unpickable_exception,
    'task_with_pickable_exception': tasks.task_with_pickable_exception,
}


@app.route('/')
def hello_world():
    task_name = request.args.get('task_name')
    wait_time = request.args.get('wait_time')
    countdown = request.args.get('countdown')
    queue = request.args.get('queue')
    serializer = request.args.get('serializer')
    priority = request.args.get('priority')
    print('request.base_url', request.base_url)
    print('request.url_root', request.url_root)

    if not task_name:
        html_tasks = '<ul>'
        for available_task in TASK_MAP:
            html_tasks += f'<li><a href="?task_name={available_task}&wait_time=1" target=_blank>{available_task}</a></li>'
        html_tasks += '</ul>'
        return f'''
            Specify task task_name:
            <br />
            <code>?task_name=<task_name>&wait_time=<wait_time>&countdown=<countdown><code>
            <br />
            <br />
            <div>Example:</div>
            <a href="{request.url_root}?task_name=simple_task&wait_time=1">{request.url_root}?task_name=simple_task&wait_time=1<a>
            <br />
            <br />
            <b>Available tasks (all with <code>wait_time=1</code>)</b>:
            <br />
            <div>There is additional param: queue. Add it to specify the exact queue the task should be sent to</div>
            <div>Example:</div>
            <div>
                <a href="{request.url_root}?task_name=simple_task&wait_time=1&queue=dedicated">{request.url_root}?task_name=simple_task&wait_time=1&queue=dedicated<a>
            </div>
            <br />
            <div>It is possible to specify countdown as well:</div>
            <div><a href="{request.url_root}?task_name=simple_task&wait_time=1&countdown=10">{request.url_root}?task_name=simple_task&wait_time=1&countdown=10<a></div>
            <br />
            <br />
            <div>Specify <a href="https://docs.celeryproject.org/en/stable/userguide/calling.html#serializers">serializer</a>:</div>
            <div><a href="{request.url_root}?task_name=task_with_unpickable_exception&serializer=json">{request.url_root}?task_name=task_with_unpickable_exception&serializer=json<a></div>
            <br />
            {html_tasks}
        '''
    wait_time = int(wait_time) if wait_time else wait_time
    kwargs = {'wait_time': wait_time}

    if task_name == 'chained_aka_linked_task':
        task_func = create_chained_aka_linked_task(**kwargs)
    else:
        task_func = TASK_MAP[task_name]
    options = {}
    if queue:
        options['queue'] = queue
    if priority:
        options['priority'] = int(priority)
    if countdown:
        options['countdown'] = int(countdown)
    if serializer:
        options['serializer'] = serializer
    if task_name == 'broadcast_task':
        options['routing_key'] = 'broadcast_tasks'

    task_func.apply_async(kwargs=kwargs, **options)

    return f'''
        <div>Called {task_name}(kwargs={kwargs}, {options})</div>
        <br />
        <br />
        <div>Return <a href="/">back</a></div>
    '''
