Celery example
==============

Run
---

### Separate instances (manual docker launch)

1. Run broker

    ```bash
    make docker-redis-run
    ```

    OR

    ```bash
    make docker-rabbit-run
    ```

2. Run worker (consumer)

    ```bash
    # ======== with Redis =============

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 --without-heartbeat --prefetch-multiplier 1 -Q default,broadcast_tasks" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 --without-heartbeat --prefetch-multiplier 1 -Q default,advanced" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 2 -Ofair --without-heartbeat --prefetch-multiplier 1 -Q default" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 2 --without-heartbeat --prefetch-multiplier 1 -Q default" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 2 -O default --without-heartbeat -Q default" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 -O default --without-heartbeat -Q default" make docker-worker-run
    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 -O fair --without-heartbeat -Q default" make docker-worker-run
    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 -O fair --prefetch-multiplier 1 --without-heartbeat -Q default" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 -O fair -Q default" make docker-worker-run
    DOCKER_WORKER_COUNT=2 CELERY_PARAMS="-c 1 -O fair -Q default" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 -E -Q default" make docker-worker-run

    # ======== with RabbitMQ =============
    DOCKER_WORKER_COUNT=1 CELERY_BROKER_NAME="rabbitmq" CELERY_PARAMS="-c 1 -Q default" make docker-worker-run

    DOCKER_WORKER_COUNT=1 CELERY_BROKER_NAME="rabbitmq" CELERY_PARAMS="-c 1 -O fair -Q default,broadcast_tasks" make docker-worker-run
    DOCKER_WORKER_COUNT=1 CELERY_BROKER_NAME="rabbitmq" CELERY_PARAMS="-c 1 --prefetch-multiplier 1 -Q default,broadcast_tasks" make docker-worker-run
    ```

    Second worker (and so on, just increment `DOCKER_WORKER_COUNT`)
    ```bash
    DOCKER_WORKER_COUNT=2 CELERY_PARAMS="-c 1 --without-heartbeat -Q critical,broadcast_tasks" make docker-worker-run
    ```

    Third
    ```bash
    DOCKER_WORKER_COUNT=3 CELERY_PARAMS="-c 1 --without-heartbeat -Q advanced,broadcast_tasks" make docker-worker-run
    ```

    Fourth
    ```bash
    DOCKER_WORKER_COUNT=4 CELERY_PARAMS="-c 1 --without-heartbeat -Q dedicated,broadcast_tasks" make docker-worker-run
    ```

    ##### Worker with systemd

    ```bash
    # Start container
    DOCKER_WORKER_COUNT=1 make docker-systemd-worker-run
    # Connect to container
    DOCKER_WORKER_COUNT=1 make docker-systemd-worker-shell
    # Connect to container as root
    DOCKER_WORKER_COUNT=1 DOCKER_CONTAINER_USER=root make docker-systemd-worker-shell

    # Inside container
    CELERY_PARAMS="-c 1 --without-heartbeat -Q default,broadcast_tasks" /app/scripts/entrypoint.sh make -C /app run-worker

    systemctl daemon-reload
    systemctl start celery
    systemctl status celery
    systemctl stop celery

    # Stop container
    DOCKER_WORKER_COUNT=1 make docker-systemd-worker-stop
    ```

3. Run celery beat (optional)

    ```bash
    make docker-celery-beat
    ```

4. Run server (producer)

    ```bash
    # with redis broker (by default)
    make docker-app-run

    # with rabbitmq
    make docker-app-run-rabbit
    ```

Other commands
--------------

- Redis client

    ```bash
    make docker-redis-cli
    ```

- Redis monitor (see every command executed by redis)

    ```bash
    make docker-redis-monitor
    ```

    Useful commands:
    ```bash
    HGETALL unacked
    ZRANGE unacked_index 0 -1
    LRANGE default 0 -1
    ```

- Worker bash shell

    ```bash
    make docker-worker-shell
    ```

- Run bash shell in already running worker container

    ```bash
    DOCKER_WORKER_COUNT=1 make docker-worker-exec-shell
    ```

- Worker without heartbeat (useful to monitor redis commands, heartbeat adds noise)

    ```bash
    CELERY_PARAMS="--without-heartbeat" make docker-worker-run
    ```

- Run single process of worker (not the number of CPUs which is the default behaviour)

    ```bash
    CELERY_PARAMS="-c 1" make docker-worker-run
    # combined with no heartbeat
    CELERY_PARAMS="-c 1 --without-heartbeat" make docker-worker-run
    ```

- App bash shell

    ```bash
    make docker-app-shell
    ```

    Connect to existing container

    ```bash
    make docker-app-exec-shell
    ```

    Start django shell inside container
    ```bash
    make -C /app shell
    ```

    Start celery task from shell
    ```python
    import tasks
    result = tasks.simple_task.delay()

    result.get()  # if result backend is not configured - "NotImplementedError: No result backend is configured." will be raised
    ```

    Create chained tasks

    ```python
    import tasks
    si = tasks.simple_task.si(wait_time=10)
    # si = tasks.task_with_exception.si(wait_time=10)
    si.link(tasks.second_simple_task.si(wait_time=3))
    si.delay()
    ```

- Inspect celery (worker must be already running)

    ```bash
    CELERY_PARAMS="status" make docker-celery-command
    CELERY_PARAMS="inspect stats" make docker-celery-command
    CELERY_PARAMS="inspect active_queues" make docker-celery-command  # The most interesting
    CELERY_PARAMS="shell" make docker-celery-command
    CELERY_PARAMS="help" make docker-celery-command
    ```

    Inside container's shell (just faster):
    ```bash
    make docker-app-exec-shell
    # inside shell
    cd /app
    CELERY_PARAMS="status" make celery-command
    CELERY_PARAMS="inspect stats" make celery-command
    CELERY_PARAMS="inspect active_queues" make celery-command
    ```

    Using inspect from python:
    ```bash
    make docker-app-exec-shell
    make -C /app shell
    ```
    In python shell
    ```python
    from celery_app import app
    i = app.control.inspect()  # Inspect all nodes.
    i.registered()
    i.active()
    i.scheduled()
    i.reserved()
    ```

    Check messages in redis queue:
    ```bash
    make docker-redis-cli
    # inside redis cli, "default" is the queue name
    llen default
    # or show the values
    LRANGE default 0 -1
    ```

- Watch for celery events

    ```bash
    DOCKER_WORKER_COUNT=99 CELERY_PARAMS="events" make docker-celery-command
    ```

- Stop celery worker process

    ```bash
    docker stop -t 0 celery-example-redis-worker1
    ```

- Disconnect celery worker from network

    ```bash
    docker network disconnect bridge celery-example-redis-worker1
    ```

- Manually start and stop celery multi inside docker

    ```bash
    # connect to worker's shell
    make docker-worker-shell

    # being inside docker

    # start celery
    ENV=venv_debian CELERY_PARAMS="-c 1 --without-heartbeat -Q default,broadcast_tasks" make celery-multi-start

    # stop celery
    ENV=venv_debian CELERY_PARAMS="-c 1 --without-heartbeat -Q default,broadcast_tasks" make celery-multi-stop

    # reload celery
    ENV=venv_debian CELERY_PARAMS="-c 1 --without-heartbeat -Q default,broadcast_tasks" make celery-multi-reload
    ```

- Show events

    ```bash
    DOCKER_WORKER_COUNT=99 CELERY_PARAMS="events" make docker-celery-command
    ```

- Run worker with enabled events

    ```bash
    DOCKER_WORKER_COUNT=1 CELERY_PARAMS="-c 1 --without-heartbeat -E --prefetch-multiplier 1 -Q default,broadcast_tasks" make docker-worker-run
    ```

- Run real time monitor

    ```bash
    make docker-real-time-monitor
    ```

- Run camera monitor

    ```bash
    make docker-camera-monitor
    ```

- Run shell (bash) for rabbitMQ node

    ```bash
    make docker-rabbit-shell
    ```

- Run rabbitmq admin

    First, start rabbitmq itself

    ```bash
    make docker-rabbit-run
    ```

    In another terminal, connect to rabbitmq server and enable rabbitmq_management:
    ```bash
    make docker-rabbit-shell

    # inside docker
    rabbitmq-plugins enable rabbitmq_management
    ```

    Then on you host machine (use your own python):
    ```bash
    python rabbitmq/scripts/rabbitmqadmin help subcommands

    python rabbitmq/scripts/rabbitmqadmin list queues

    python rabbitmq/scripts/rabbitmqadmin list exchanges
     ```

Server (app, producer) examples
-------------------------------

- Launch a task

    http://localhost:5000/?task_name=some_task&task_arg=10
