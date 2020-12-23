from celery_app import app


def my_monitor(app):
    state = app.events.State()

    def announce_tasks(event):
        """
        Log event.

        Event example:

        ```python
        {
            'hostname': 'gen13@f6a83b10c017',
            'utcoffset': 0,
            'pid': 13,
            'clock': 11,
            'uuid': '5c9ce806-8a1d-4641-a270-ef41f29391cb',
            'root_id': '5c9ce806-8a1d-4641-a270-ef41f29391cb',
            'parent_id': None,
            'name': 'tasks.regular.simple_task',
            'args': '()',
            'kwargs': "{'wait_time': 10}",
            'retries': 0,
            'eta': None,
            'expires': None,
            'queue': 'default',
            'exchange': '',
            'routing_key': 'default',
            'timestamp': 1607688290.2697067,
            'type': 'task-sent',
            'local_received': 1607688290.2717652,
            'state': 'PENDING',
        }
        ```
        """
        state.event(event)  # TODO: What is this?
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print(
            'TASK EVENT {event_type}: {task_name}[{task_uuid}] {task_info}'.format(
                event_type=event['type'],
                task_name=task.name,
                task_uuid=task.uuid,
                task_info=task.info(),
            )
        )

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-sent': announce_tasks,
                'task-received': announce_tasks,
                'task-started': announce_tasks,
                'task-succeeded': announce_tasks,
                'task-rejected': announce_tasks,
                'task-revoked': announce_tasks,
                'task-retried': announce_tasks,
                'task-failed': announce_tasks,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)  # TODO: what is "wakeup" ?


if __name__ == '__main__':
    my_monitor(app)
