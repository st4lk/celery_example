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

# Redis

docker-redis-build:
	docker build -t $(DOCKER_REDIS_NAME) redis/

docker-redis-run: docker-redis-build
	docker run -it --rm --name $(DOCKER_REDIS_NAME) $(DOCKER_REDIS_NAME) $(DOCKER_COMMAND)

docker-redis-cli:
	docker exec -it $(DOCKER_REDIS_NAME) redis-cli -h $(REDIS_HOST)

docker-redis-monitor:
	docker exec -it $(DOCKER_REDIS_NAME) redis-cli -h $(REDIS_HOST) monitor

# Worker

docker-worker-build:
	docker build -t $(DOCKER_WORKER_NAME) app/

docker-worker: docker-worker-build
	docker run -it --rm --name $(DOCKER_WORKER_NAME)${DOCKER_WORKER_COUNT} -v $(PWD)/app:/app \
	-e REDIS_HOST=$(REDIS_HOST) \
	-e REDIS_PORT=$(REDIS_PORT) \
	-e CELERY_PARAMS="$(CELERY_PARAMS)" \
	$(DOCKER_WORKER_NAME) $(DOCKER_COMMAND)

docker-worker-run:
	CELERY_PARAMS="$(CELERY_PARAMS)" DOCKER_COMMAND="make run-worker" $(MAKE) docker-worker

docker-worker-shell:
	DOCKER_COMMAND="bash" $(MAKE) docker-worker

docker-worker-exec-shell:
	docker exec -it $(DOCKER_WORKER_NAME)$(DOCKER_WORKER_COUNT) bash

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

docker-app-run: docker-app-build
	docker run -p $(SERVER_PORT):$(SERVER_PORT) -it --rm --name $(DOCKER_APP_NAME) -v $(PWD)/app:/app \
	-e REDIS_HOST=$(REDIS_HOST) \
	-e REDIS_PORT=$(REDIS_PORT) \
	$(DOCKER_APP_NAME) $(DOCKER_COMMAND)

docker-app-shell:
	DOCKER_COMMAND="bash" $(MAKE) docker-app-run

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
