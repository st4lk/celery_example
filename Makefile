DOCKER_APP_NAME ?= celery-example-redis-app
DOCKER_WORKER_NAME ?= celery-example-redis-worker
DOCKER_REAL_TIME_MONITOR_NAME ?= celery-real-time-monitor
DOCKER_CAMERA_MONITOR_NAME ?= celery-camera-monitor
DOCKER_WORKER_SYSTEMD_NAME ?= celery-example-redis-worker-systemd
DOCKER_REDIS_NAME ?= celery-example-redis-broker
DOCKER_CONTAINER_USER ?= appuser
DOCKER_COMMAND ?=
REDIS_HOST ?= `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(DOCKER_REDIS_NAME)`
REDIS_PORT ?= 6379
SERVER_PORT ?= 5000

DOCKER_RABBITMQ_NAME ?= celery-example-rabbitmq-broker
RABBITMQ_HOSTNAME ?= my-rabbit
RABBITMQ_DEFAULT_VHOST ?= my-rabbit
RABBITMQ_HOST ?= `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(DOCKER_RABBITMQ_NAME)`
RABBITMQ_PORT ?= 5672
RABBITMQ_DEFAULT_USER ?= guest
RABBITMQ_DEFAULT_PASS ?= guest

CELERY_BROKER_NAME ?= redis

# Redis

docker-redis-build:
	docker build -t $(DOCKER_REDIS_NAME) redis/

docker-redis-run: docker-redis-build
	docker run -it --rm --name $(DOCKER_REDIS_NAME) $(DOCKER_REDIS_NAME) $(DOCKER_COMMAND)

docker-redis-cli:
	docker exec -it $(DOCKER_REDIS_NAME) redis-cli -h $(REDIS_HOST)

docker-redis-monitor:
	docker exec -it $(DOCKER_REDIS_NAME) redis-cli -h $(REDIS_HOST) monitor

# RabbitMQ

docker-rabbit-build:
	docker build -t $(DOCKER_RABBITMQ_NAME) rabbitmq/

docker-rabbit-run: docker-rabbit-build
	docker run -p 15672:15672 -it --rm --hostname $(RABBITMQ_HOSTNAME) -v $(PWD)/rabbitmq/scripts:/scripts \
	-e RABBITMQ_DEFAULT_USER=$(RABBITMQ_DEFAULT_USER) \
	-e RABBITMQ_DEFAULT_PASS=$(RABBITMQ_DEFAULT_PASS) \
	-e RABBITMQ_DEFAULT_VHOST=$(RABBITMQ_DEFAULT_VHOST) \
	--name $(DOCKER_RABBITMQ_NAME) $(DOCKER_RABBITMQ_NAME) $(DOCKER_COMMAND)

docker-rabbit-shell:
	docker exec -it $(DOCKER_RABBITMQ_NAME) bash

# Worker

docker-worker-build:
	docker build -t $(DOCKER_WORKER_NAME) app/

docker-worker: docker-worker-build
	docker run -it --rm --name $(DOCKER_WORKER_NAME)${DOCKER_WORKER_COUNT} -v $(PWD)/app:/app \
	-e REDIS_HOST=$(REDIS_HOST) \
	-e REDIS_PORT=$(REDIS_PORT) \
	-e RABBITMQ_HOST=$(RABBITMQ_HOST) \
	-e RABBITMQ_PORT=$(RABBITMQ_PORT) \
	-e RABBITMQ_DEFAULT_VHOST=$(RABBITMQ_DEFAULT_VHOST) \
	-e RABBITMQ_DEFAULT_USER=$(RABBITMQ_DEFAULT_USER) \
	-e RABBITMQ_DEFAULT_PASS=$(RABBITMQ_DEFAULT_PASS) \
	-e CELERY_BROKER_NAME=$(CELERY_BROKER_NAME) \
	-e CELERY_PARAMS="$(CELERY_PARAMS)" \
	$(DOCKER_WORKER_NAME) $(DOCKER_COMMAND)

docker-worker-run:
	CELERY_PARAMS="$(CELERY_PARAMS)" DOCKER_COMMAND="make run-worker" $(MAKE) docker-worker

docker-worker-shell:
	DOCKER_COMMAND="bash" $(MAKE) docker-worker

docker-worker-exec-shell:
	docker exec -it $(DOCKER_WORKER_NAME)$(DOCKER_WORKER_COUNT) bash

docker-celery-beat:
	CELERY_PARAMS="$(CELERY_PARAMS)" DOCKER_COMMAND="make run-celery-beat" $(MAKE) docker-worker

docker-celery-command:
	CELERY_PARAMS="$(CELERY_PARAMS)" DOCKER_COMMAND="make celery-command" $(MAKE) docker-worker

# Worker with systemd
docker-systemd-worker-build:
	docker build --rm -t $(DOCKER_WORKER_SYSTEMD_NAME) -f app/Dockerfile.csd app/

docker-systemd-worker-run: docker-systemd-worker-build
	docker run --privileged -d --rm --name $(DOCKER_WORKER_SYSTEMD_NAME)$(DOCKER_WORKER_COUNT) -v $(PWD)/app:/app \
	-v /sys/fs/cgroup:/sys/fs/cgroup:ro \
	-e REDIS_HOST=$(REDIS_HOST) \
	-e REDIS_PORT=$(REDIS_PORT) \
	$(DOCKER_WORKER_SYSTEMD_NAME)

docker-systemd-worker-shell:
	docker exec -it --user $(DOCKER_CONTAINER_USER) $(DOCKER_WORKER_SYSTEMD_NAME)$(DOCKER_WORKER_COUNT) bash

docker-systemd-worker-stop:
	docker stop $(DOCKER_WORKER_SYSTEMD_NAME)$(DOCKER_WORKER_COUNT)


# App

docker-app-build:
	docker build -t $(DOCKER_APP_NAME) app/

docker-app-run-base: docker-app-build
	docker run -p $(SERVER_PORT):$(SERVER_PORT) -it --rm --name $(DOCKER_APP_NAME) -v $(PWD)/app:/app \
	-e REDIS_HOST=$(REDIS_HOST) \
	-e REDIS_PORT=$(REDIS_PORT) \
	-e RABBITMQ_HOST=$(RABBITMQ_HOST) \
	-e RABBITMQ_PORT=$(RABBITMQ_PORT) \
	-e RABBITMQ_DEFAULT_VHOST=$(RABBITMQ_DEFAULT_VHOST) \
	-e RABBITMQ_DEFAULT_USER=$(RABBITMQ_DEFAULT_USER) \
	-e RABBITMQ_DEFAULT_PASS=$(RABBITMQ_DEFAULT_PASS) \
	-e CELERY_BROKER_NAME=$(CELERY_BROKER_NAME) \
	$(DOCKER_APP_NAME) $(DOCKER_COMMAND)

docker-app-run:
	CELERY_BROKER_NAME=redis RABBITMQ_HOST="" $(MAKE) docker-app-run-base

docker-app-run-rabbit:
	CELERY_BROKER_NAME=rabbitmq REDIS_HOST="" $(MAKE) docker-app-run-base

docker-app-shell:
	DOCKER_COMMAND="bash" $(MAKE) docker-app-run-base

docker-app-exec-shell:
	docker exec -it $(DOCKER_APP_NAME) bash

# May be useful because of this bottle issue: https://github.com/bottlepy/bottle/issues/814
docker-app-stop:
	docker stop -t 0 $(DOCKER_APP_NAME)


# Monitor

docker-real-time-monitor:
	DOCKER_WORKER_NAME="$(DOCKER_REAL_TIME_MONITOR_NAME)" DOCKER_COMMAND="make run-real-time-monitor" $(MAKE) docker-worker

docker-camera-monitor:
	DOCKER_WORKER_NAME="$(DOCKER_CAMERA_MONITOR_NAME)" DOCKER_COMMAND="make run-camera-monitor" $(MAKE) docker-worker
